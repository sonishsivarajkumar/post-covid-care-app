from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)  # new


# Patient Register api
class Patient(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)

    def __repr__(self):
        return '<Patient %s>' % self.first_name


class PatientSchema(ma.Schema):
    class Meta:
        fields = (
            'patient_id', 'first_name', 'last_name', 'email', 'password', 'age', 'gender', 'height_cm', 'weight_kg')
        model = Patient


patient_schema = PatientSchema()
patients_schema = PatientSchema(many=True)


class PatientListResource(Resource):
    def get(self):
        records = Patient.query.all()
        return patients_schema.dump(records)

    def post(self):
        new_post = Patient(
            patient_id=request.json['patient_id'],
            first_name=request.json['first_name'],
            last_name=request.json['last_name'],
            email=request.json['email'],
            password=request.json['password'],
            age=request.json['age'],
            gender=request.json['gender'],
            height_cm=request.json['height_cm'],
            weight_kg=request.json['weight_kg']
        )
        db.session.add(new_post)
        db.session.commit()
        return patient_schema.dump(new_post)


class PatientResource(Resource):
    def get(self, patient_id):
        record = Patient.query.get_or_404(patient_id)
        return patient_schema.dump(record)

    def delete(self, patient_id):
        record = Patient.query.get_or_404(patient_id)
        db.session.delete(record)
        db.session.commit()
        return '', 204


api.add_resource(PatientResource, '/patient/<int:patient_id>')
api.add_resource(PatientListResource, '/patients')


# History api
class History(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    date_of_onset_of_symptoms = db.Column(db.String(50))
    date_of_diagnosis = db.Column(db.String(50))
    initial_symptoms = db.Column(db.String(50))
    date_of_pcr_negative = db.Column(db.String(50))
    comorbidities = db.Column(db.String(50))
    vaccination_status = db.Column(db.String(50))
    hospitalization_status = db.Column(db.Boolean)
    icu = db.Column(db.Boolean)

    def __repr__(self):
        return '<History %s>' % self.initial_symptoms


class HistorySchema(ma.Schema):
    class Meta:
        fields = (
            "patient_id", "date_of_onset_of_symptoms", "date_of_diagnosis", "initial_symptoms", "date_of_pcr_negative",
            "comorbidities", "vaccination_status", "hospitalization_status", "icu")
        model = History


history_schema = HistorySchema()
historys_schema = HistorySchema(many=True)


class HistoryListResource(Resource):
    def get(self):
        records = History.query.all()
        return historys_schema.dump(records)

    def post(self):
        new_post = History(
            patient_id=request.json['patient_id'],
            date_of_onset_of_symptoms=request.json['date_of_onset_of_symptoms'],
            date_of_diagnosis=request.json['date_of_diagnosis'],
            initial_symptoms=request.json['first_symptoms'],
            date_of_pcr_negative=request.json['date_of_pcr_negative'],
            comorbidities=request.json['comorbidities'],
            vaccination_status=request.json['vaccination_status'],
            hospitalization_status=request.json['hospitalization'],
            icu=request.json['icu'])
        db.session.add(new_post)
        db.session.commit()
        return history_schema.dump(new_post)


class HistoryResource(Resource):
    def get(self, patient_id):
        record = History.query.get_or_404(patient_id)
        return history_schema.dump(record)

    def patch(self, patient_id):
        record = History.query.get_or_404(patient_id)

        if 'date_of_onset_of_symptoms' in request.json:
            record.date_of_onset_of_symptoms = request.json['date_of_onset_of_symptoms']
        if 'date_of_diagnosis' in request.json:
            record.date_of_diagnosis = request.json['date_of_diagnosis']
        if 'initial_symptoms' in request.json:
            record.initial_symptoms = request.json['initial_symptoms']
        if 'date_of_pcr_negative' in request.json:
            record.date_of_pcr_negative = request.json['date_of_pcr_negative']
        if 'comorbidities' in request.json:
            record.comorbidities = request.json['comorbidities']
        if 'vaccination_status' in request.json:
            record.vaccination_status = request.json['vaccination_status']
        if 'hospitalization_status' in request.json:
            record.hospitalization_status = request.json['hospitalization_status']
        if 'icu' in request.json:
            record.icu = request.json['icu']

        db.session.commit()
        return history_schema.dump(record)

    def delete(self, patient_id):
        record = History.query.get_or_404(patient_id)
        db.session.delete(record)
        db.session.commit()
        return '', 204


api.add_resource(HistoryResource, '/history/<int:patient_id>')
api.add_resource(HistoryListResource, '/historys')


# Current State API
class CurrentState(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    vitals_bp = db.Column(db.String(50))
    vitals_pulse = db.Column(db.Integer)
    vitals_oxygen_level = db.Column(db.Float)
    vitals_temperature = db.Column(db.Float)
    current_symptoms = db.Column(db.String(50))

    def __repr__(self):
        return '<CurrentState %s>' % self.current_symptoms


class CurrentStateSchema(ma.Schema):
    class Meta:
        fields = (
            "patient_id", "vitals_bp", "vitals_pulse", "vitals_oxygen_level",
            "vitals_temperature", "current_symptoms")
        model = CurrentState


currentstate_schema = CurrentStateSchema()
currentstates_schema = CurrentStateSchema(many=True)


class CurrentStateListResource(Resource):
    def get(self):
        records = CurrentState.query.all()
        return currentstates_schema.dump(records)

    def post(self):
        new_post = CurrentState(
            patient_id=request.json['patient_id'],
            vitals_bp=request.json['vitals_bp'],
            vitals_pulse=request.json['vitals_pulse'],
            vitals_oxygen_level=request.json['vitals_oxygen_level'],
            vitals_temperature=request.json['vitals_temperature'],
            current_symptoms=request.json['current_symptoms'])
        db.session.add(new_post)
        db.session.commit()
        return currentstate_schema.dump(new_post)


class CurrentStateResource(Resource):
    def get(self, patient_id):
        record = CurrentState.query.get_or_404(patient_id)
        return currentstate_schema.dump(record)

    def delete(self, patient_id):
        record = CurrentState.query.get_or_404(patient_id)
        db.session.delete(record)
        db.session.commit()
        return '', 204


api.add_resource(CurrentStateResource, '/currentstate/<int:patient_id>')
api.add_resource(CurrentStateListResource, '/currentstates')


# PCFS Questionnaire API
class PcfsQuestionnaire(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    question_1 = db.Column(db.Boolean)
    question_2 = db.Column(db.Boolean)
    question_3 = db.Column(db.Boolean)
    question_4 = db.Column(db.Boolean)

    def __repr__(self):
        return '<PcfsQuestionnaire %s>' % self.question_1


class PcfsQuestionnaireSchema(ma.Schema):
    class Meta:
        fields = (
            "patient_id", "question_1", "question_2", "question_3", "question_4")
        model = PcfsQuestionnaire


question_schema = PcfsQuestionnaireSchema()
questions_schema = PcfsQuestionnaireSchema(many=True)


class PcfsQuestionnaireListResource(Resource):
    def get(self):
        records = PcfsQuestionnaire.query.all()
        return questions_schema.dump(records)

    def post(self):
        new_post = PcfsQuestionnaire(
            patient_id=request.json['patient_id'],
            question_1=request.json['question_1'],
            question_2=request.json['question_2'],
            question_3=request.json['question_3'],
            question_4=request.json['question_4'])
        db.session.add(new_post)
        db.session.commit()
        return question_schema.dump(new_post)


class PcfsQuestionnaireResource(Resource):
    def get(self, patient_id):
        record = PcfsQuestionnaire.query.get_or_404(patient_id)
        return question_schema.dump(record)

    def delete(self, patient_id):
        record = PcfsQuestionnaire.query.get_or_404(patient_id)
        db.session.delete(record)
        db.session.commit()
        return '', 204


api.add_resource(PcfsQuestionnaireResource, '/question/<int:patient_id>')
api.add_resource(PcfsQuestionnaireListResource, '/questions')


# class RegisterUser(Resource):
#     def get(self):
#         records = User.query.all()
#         return users_schema.dump(records)
#
#     def post(self):
#         new_post = User(
#             patient_id=request.json['patient_id'],
#             username=request.json['username'],
#             password=request.json['password'])
#         data = User.query.filter_by(username=new_post.username).first()
#         if data is not None:
#             return jsonify(message="Username already taken")
#         else:
#             db.session.add(new_post)
#             db.session.commit()
#             return user_schema.dump(new_post)
#
#
# class LoginUser(Resource):
#     def post(self):
#         new_post = User(
#             username=request.json['username'],
#             password=request.json['password'])
#         data = User.query.filter_by(username=new_post.username, password=new_post.password).first()
#         if data is not None:
#             return jsonify(message="you have logged in")
#         else:
#             return jsonify(message="invalid username or password")
#
#
# api.add_resource(RegisterUser, '/register')
# api.add_resource(LoginUser, '/login')




class ClassifyPatientResource(Resource):
    def get(self):

        query = 'SELECT * FROM Patient p INNER JOIN History h USING(patient_id) \
                        INNER JOIN current_state USING(patient_id) INNER JOIN Pcfs_Questionnaire USING(patient_id)'
        result = db.session.execute(query).fetchall()

        response_list = []
        for r in result:

            if not r['question_1']:
                score = 4
            elif r['question_2']:
                score = 3
            elif not r['question_3']:
                score = 0
            elif not r['question_4']:
                score = 1
            else:
                score = 2

            pcfs = score
            res = 'No'
            bp_sys, bp_dias = r['vitals_bp'].split('/')
            bp1 = int(bp_sys)
            bp2 = int(bp_dias)
            pulse = int(r['vitals_pulse'])
            temp = int(r['vitals_temperature'])
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

            current_symptoms = r['current_symptoms'].split(',')
            comorbidities = r['comorbidities'].split(',')
            set1 = set(danger_symptoms)
            set2 = set(flagged_comorbidities)

            list1 = [value for value in current_symptoms if value in set1]
            list2 = [value for value in comorbidities if value in set2]

            if (bp1 > 140 and bp2 > 90) or pulse > 100 or temp > 38:
                res = 'Yes'

            if (len(list1) >= 1) or (pcfs >= 1) or (len(list2) >= 1):
                res = 'Yes'

            response = {'patient_id': r['patient_id'], 'Expert_intervention_required': res, 'Location': 'US',
                        'Specialties_to_consult': 'Internal medicine, Family medicine, General practice,'
                                                  ' Emergency medicine'}
            response_list.append(response)

        ResponseSchema = Schema.from_dict(
            {"patient_id": fields.Int(), "Expert_intervention_required": fields.Str(), "Location": fields.Str(),
             "Specialties_to_consult": fields.Str()})
        schema = ResponseSchema(many=True)
        return schema.dump(response_list)


api.add_resource(ClassifyPatientResource, '/classify')

class User(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))

    def __repr__(self):
        return '<User %s>' % self.username


class UserSchema(ma.Schema):
    class Meta:
        fields = ('patient_id', 'username', 'password')
        model = User


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class RegisterUser(Resource):
    def get(self):
        records = User.query.all()
        return users_schema.dump(records)

    def post(self):
        new_post = User(
            patient_id=request.json['patient_id'],
            username=request.json['username'],
            password=request.json['password'])
        data = User.query.filter_by(username=new_post.username).first()
        if data is not None:
            abort(
                409,
                "Username already exists"
            )
        else:
            db.session.add(new_post)
            db.session.commit()
            return user_schema.dump(new_post), 201



class LoginUser(Resource):
    def post(self):
        new_post = User(
            username=request.json['username'],
            password=request.json['password'])
        data = User.query.filter_by(username=new_post.username, password=new_post.password).first()
        if data is not None:
            return "you have logged in", 201
        else:
            abort(
                403,
                "Invalid username or password"
            )

api.add_resource(RegisterUser, '/register')
api.add_resource(LoginUser, '/login')

db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3015)
