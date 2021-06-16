from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)  # new


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.String(255))

    patient_id = db.Column(db.Integer)
    date_of_onset_of_symptoms = db.Column(db.String(50))
    first_symptoms = db.Column(db.String(50))
    date_of_pcr_negative = db.Column(db.String(50))
    comorbidities = db.Column(db.String(50))
    vaccination_status = db.Column(db.String(50))
    hospitalization = db.Column(db.String(50))
    icu = db.Column(db.String(50))

    def __repr__(self):
        return '<Post %s>' % self.title


# db.create_all()

class PostSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "content", "patient_id", "date_of_onset_of_symptoms", "first_symptoms", "date_of_pcr_negative", "comorbidities", "vaccination_status", "hospitalization", "icu")
        model = Post


post_schema = PostSchema()
posts_schema = PostSchema(many=True)


class PostListResource(Resource):
    def get(self):
        posts = Post.query.all()
        return posts_schema.dump(posts)

    def post(self):
        new_post = Post(
            title=request.json['title'],
            content=request.json['content'],
            patient_id=request.json['patient_id'],
            date_of_onset_of_symptoms=request.json['date_of_onset_of_symptoms'],
            first_symptoms=request.json['first_symptoms'],
            date_of_pcr_negative=request.json['date_of_pcr_negative'],
            comorbidities=request.json['comorbidities'],
            vaccination_status=request.json['vaccination_status'],
            hospitalization=request.json['hospitalization'],
            icu=request.json['icu'])
        db.session.add(new_post)
        db.session.commit()
        return post_schema.dump(new_post)


class PostResource(Resource):
    def get(self, post_id):
        post = Post.query.get_or_404(post_id)
        return post_schema.dump(post)

    # def patch(self, post_id):
    #     post = Post.query.get_or_404(post_id)
    #
    #     if 'title' in request.json:
    #         post.title = request.json['title']
    #     if 'content' in request.json:
    #         post.content = request.json['content']
    #
    #     db.session.commit()
    #     return post_schema.dump(post)

    def delete(self, post_id):
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return '', 204


api.add_resource(PostResource, '/posts/<int:post_id>')
api.add_resource(PostListResource, '/posts')
# ...

if __name__ == '__main__':
    app.run(debug=True)
