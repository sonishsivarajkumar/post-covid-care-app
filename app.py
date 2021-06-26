from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
from sqlalchemy import insert, update
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)  # new


# PatientDetails api
class PatientDetails(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    date_of_onset_of_symptoms = db.Column(db.String(50))
    date_of_diagnosis = db.Column(db.String(50))
    initial_symptoms = db.Column(db.JSON)
    date_of_pcr_negative = db.Column(db.String(50))
    comorbidities = db.Column(db.JSON)
    vaccination_status = db.Column(db.String(50))
    hospitalization_status = db.Column(db.Boolean)
    icu = db.Column(db.Boolean)
    vitals_bp = db.Column(db.String(50))
    vitals_pulse = db.Column(db.Integer)
    vitals_oxygen_level = db.Column(db.Float)
    vitals_temperature = db.Column(db.Float)
    current_symptoms = db.Column(db.JSON)
    question_1 = db.Column(db.Boolean)
    question_2 = db.Column(db.Boolean)
    question_3 = db.Column(db.Boolean)
    question_4 = db.Column(db.Boolean)

    def __repr__(self):
        return '<Patient %s>' % self.gender


class PatientDetailsSchema(ma.Schema):
    class Meta:
        fields = (
            'patient_id', 'age', 'gender', 'height_cm', 'weight_kg',
            'date_of_onset_of_symptoms', 'date_of_diagnosis', 'initial_symptoms', 'date_of_pcr_negative',
            'comorbidities', 'vaccination_status', 'hospitalization_status', 'icu', "vitals_bp",
            "vitals_pulse", "vitals_oxygen_level", "vitals_temperature", "current_symptoms",
            "question_1", "question_2", "question_3", "question_4")
        model = PatientDetails


patient_schema = PatientDetailsSchema()
patients_schema = PatientDetailsSchema(many=True)


class Recommendation(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    hcp_required = db.Column(db.Boolean)
    hcp_required_reasons = db.Column(db.JSON)
    location = db.Column(db.JSON)
    specialties_to_consult = db.Column(db.JSON)

    def __repr__(self):
        return '<Recommendation %s>' % self.hcp_required


class RecommendationSchema(ma.Schema):
    class Meta:
        fields = ('patient_id', 'hcp_required', 'hcp_required_reasons', 'location', 'specialties_to_consult')
        model = Recommendation


recommend_schema = RecommendationSchema()
recommends_schema = RecommendationSchema(many=True)


class RecommendationListResource(Resource):
    def get(self):
        records = Recommendation.query.all()
        return recommends_schema.dump(records)


class RecommendationResource(Resource):
    def get(self, patient_id):
        record = Recommendation.query.get_or_404(patient_id)
        return recommend_schema.dump(record)


api.add_resource(RecommendationListResource, '/recommends')
api.add_resource(RecommendationResource, '/recommend/<int:patient_id>')


def calc_pcfs_score(**d):
    if not d['question_1']:
        score = 4
    elif d['question_2']:
        score = 3
    elif not d['question_3']:
        score = 0
    elif not d['question_4']:
        score = 1
    else:
        score = 2
    return score


def patient_classifier(**r):
    pcfs = calc_pcfs_score(**r)
    res = False
    warning = []
    specialties = ['Internal medicine', 'Family medicine', 'General practice', 'Emergency Medicine']
    location = 'United States'
    bp_sys, bp_dias = r['vitals_bp'].split('/')
    bp1 = int(bp_sys)
    bp2 = int(bp_dias)
    pulse = int(r['vitals_pulse'])
    temp = int(r['vitals_temperature'])
    o2 = int(r['vitals_oxygen_level'])
    danger_symptoms = ['Longstanding fatigue', 'Shortness of breath', 'Recurrent/longstanding Cough',
                       'Joint pain',
                       'Chest Pain', 'Headache', 'Skin rashes', 'Hair loss',
                       'Depression, anxiety, or mood changes',
                       'Memory and concentration problems', 'PTSD (Post traumatic stress disorder)',
                       'Racing heart beat/Palpitations/Heart rate and Rhythm Disorders',
                       'Inability to sleep properly/Insomnia', 'New onset Diabetes mellitus',
                       'High sugar levels/Impaired glycemic control', 'Heart attack/Acute coronary syndromes',
                       'Blood clots/Hypercoagulation disorders',
                       'Tingling sensation in hands/ feet/ Neuropathy',
                       'Numbness of body parts', 'Brain fog (Difficulty thinking straight)',
                       'Lungs fibrosis/Lung complications', 'Worsening of pre-existing kidney disorder',
                       'Recurring/longstanding fever', 'Recurrent/longstanding loose motions',
                       'Severe stomach pain',
                       'Blackening/discoloration of fingertips/toes']
    flagged_comorbidities = ['Diabetes Mellitus', 'Hypertension', 'High BP', 'Heart disease', 'Asthma', 'COPD',
                             'Chronic Kidney disease', 'Rheumatoid arthritis']
    current_symptoms = r['current_symptoms']
    # comorbidities = r['comorbidities'].split(',')
    comorbidities = r['comorbidities']
    set1 = set(danger_symptoms)
    set2 = set(flagged_comorbidities)
    list1 = [value for value in current_symptoms if value in set1]
    list2 = [value for value in comorbidities if value in set2]
    if (bp1 > 140 and bp2 > 90) or pulse > 100 or temp > 38 or o2 < 92:
        res = True
        warning.append('Vital signs are below normal levels!')
    if len(list1) >= 1:
        res = True
        warning.append('Serious symptoms present')
    if len(list2) >= 1:
        res = True
        warning.append('Serious comorbidities present')
    if pcfs >= 1:
        res = True
        warning.append('Functional limitations detected')
    if not res:
        specialties.clear()
        location = ''

    # saving response to recommendation table
    data = Recommendation.query.filter_by(patient_id=r['patient_id']).first()
    if data is None:
        db.session.execute(insert(Recommendation).values(patient_id=r['patient_id'], hcp_required=res,
                                                         hcp_required_reasons=warning, location=location,
                                                         specialties_to_consult=specialties))

    else:
        db.session.execute(update(Recommendation).values(hcp_required=res,
                                                         hcp_required_reasons=warning, location=location,
                                                         specialties_to_consult=specialties))
    db.session.commit()

    result = {'hcp_required': res, 'hcp_required_reasons': warning,
              'location': location, 'specialties_to_consult': specialties}
    return result


class PatientDetailsListResource(Resource):
    def get(self):
        records = PatientDetails.query.all()
        return patients_schema.dump(records)

    def post(self):
        new_post = PatientDetails(
            patient_id=request.json['patient_id'],
            age=request.json['age'],
            gender=request.json['gender'],
            height_cm=request.json['height_cm'],
            weight_kg=request.json['weight_kg'],
            date_of_onset_of_symptoms=request.json['date_of_onset_of_symptoms'],
            date_of_diagnosis=request.json['date_of_diagnosis'],
            initial_symptoms=request.json['initial_symptoms'],
            date_of_pcr_negative=request.json['date_of_pcr_negative'],
            comorbidities=request.json['comorbidities'],
            vaccination_status=request.json['vaccination_status'],
            hospitalization_status=request.json['hospitalization_status'],
            icu=request.json['icu'],
            vitals_bp=request.json['vitals_bp'],
            vitals_pulse=request.json['vitals_pulse'],
            vitals_oxygen_level=request.json['vitals_oxygen_level'],
            vitals_temperature=request.json['vitals_temperature'],
            current_symptoms=request.json['current_symptoms'],
            question_1=request.json['question_1'],
            question_2=request.json['question_2'],
            question_3=request.json['question_3'],
            question_4=request.json['question_4'])
        db.session.add(new_post)
        db.session.commit()
        p = int(request.json['patient_id'])
        record = PatientDetails.query.filter_by(patient_id=p).first()
        dic = patient_schema.dump(record)
        response = patient_classifier(**dic)

        return response


class PatientDetailsResource(Resource):
    def get(self, patient_id):
        record = PatientDetails.query.get_or_404(patient_id)
        return patient_schema.dump(record)

    def delete(self, patient_id):
        record = PatientDetails.query.get_or_404(patient_id)
        db.session.delete(record)
        db.session.commit()
        return '', 204


class UpdateDetailsResource(Resource):
    def put(self, patient_id):
        r1 = PatientDetails.query.get_or_404(patient_id)
        r2 = User.query.get_or_404(patient_id)

        r1.patient_id = request.json['patient_id']
        r2.patient_id = request.json['patient_id']
        r2.first_name = request.json['first_name']
        r2.last_name = request.json['last_name']
        r2.email = request.json['email']
        r2.password = request.json['password']
        r1.age = request.json['age']
        r1.gender = request.json['gender']
        r1.height_cm = request.json['height_cm']
        r1.weight_kg = request.json['weight_kg']
        r1.date_of_onset_of_symptoms = request.json['date_of_onset_of_symptoms']
        r1.date_of_diagnosis = request.json['date_of_diagnosis']
        r1.initial_symptoms = request.json['initial_symptoms']
        r1.date_of_pcr_negative = request.json['date_of_pcr_negative']
        r1.comorbidities = request.json['comorbidities']
        r1.vaccination_status = request.json['vaccination_status']
        r1.hospitalization_status = request.json['hospitalization_status']
        r1.icu = request.json['icu']
        r1.vitals_bp = request.json['vitals_bp']
        r1.vitals_pulse = request.json['vitals_pulse']
        r1.vitals_oxygen_level = request.json['vitals_oxygen_level']
        r1.vitals_temperature = request.json['vitals_temperature']
        r1.current_symptoms = request.json['current_symptoms']
        r1.question_1 = request.json['question_1']
        r1.question_2 = request.json['question_2']
        r1.question_3 = request.json['question_3']
        r1.question_4 = request.json['question_4']

        db.session.commit()
        dic = patient_schema.dump(r1)
        response = patient_classifier(**dic)
        return response


api.add_resource(PatientDetailsResource, '/patient_details/<int:patient_id>')
api.add_resource(PatientDetailsListResource, '/patients_details')
api.add_resource(UpdateDetailsResource, '/update/<int:patient_id>')


class User(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __repr__(self):
        return '<User %s>' % self.first_name


class UserSchema(ma.Schema):
    class Meta:
        fields = ('patient_id', 'first_name', 'last_name', 'email', 'password')
        model = User


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class RegisterUser(Resource):
    def get(self):
        records = User.query.all()
        return users_schema.dump(records)

    def post(self):
        new_post = User(
            # patient_id=request.json['patient_id'],
            first_name=request.json['first_name'],
            last_name=request.json['last_name'],
            email=request.json['email'],
            password=request.json['password'])
        data = User.query.filter_by(email=new_post.email).first()
        if data is not None:
            abort(
                409,
                "Username already exists"
            )
        else:
            db.session.add(new_post)
            db.session.commit()
            # record = User.query.all()
            e = str(request.json['email'])
            r = User.query.filter_by(email=e).first()
            response = {'patient_id': r.patient_id,
                        'first_name': r.first_name, 'last_name': r.last_name, 'email': r.email}
            ResponseSchema = Schema.from_dict(
                {"patient_id": fields.Int(), "first_name": fields.Str(), "last_name": fields.Str(),
                 "email": fields.Str()})
            schema = ResponseSchema()
            return schema.dump(response), 201


class LoginUser(Resource):
    def post(self):
        new_post = User(
            email=request.json['email'],
            password=request.json['password'])
        data = User.query.filter_by(email=new_post.email, password=new_post.password).first()
        if data is not None:
            basic_info = {'patient_id': data.patient_id, 'first_name': data.first_name,
                          'last_name': data.last_name, 'email': data.email}
            p = PatientDetails.query.filter_by(patient_id=data.patient_id).first()
            if p is not None:
                patient_details = patient_schema.dump(p)
                recommendation = recommend_schema.dump(
                    Recommendation.query.filter_by(patient_id=data.patient_id).first())
                # patient_details['comorbidities'] = patient_details['comorbidities'].split(',')
            else:
                patient_details = ''
                recommendation = ''
            response = {'basic_info': basic_info, 'patient_details': patient_details,
                        'recommendation': recommendation}
            return response, 201

        else:
            abort(
                403,
                "Invalid username or password"
            )


api.add_resource(RegisterUser, '/register')
api.add_resource(LoginUser, '/login')
db.create_all()

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
