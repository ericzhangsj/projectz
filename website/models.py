from . import db 
from flask_login import UserMixin  
from sqlalchemy import func 

followers = db.Table('followers', 
            db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_of_like = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable = False)
    post_of_like = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    comment_of_like = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete = 'CASCADE'))

class Dislike(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_of_dislike = db.Column(db.Integer, db.ForeignKey('user.id' , ondelete='CASCADE'), nullable = False)
    post_of_dislike = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))
    comment_of_dislike = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete = 'CASCADE'))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(100))

    #relationships
    posts = db.relationship('Post', backref = 'user', passive_deletes = True)
    comments = db.relationship('Comment', backref = 'user', passive_deletes = True)
    likes = db.relationship('Like', backref = 'user', passive_deletes = True)
    dislikes = db.relationship('Dislike', backref = 'user', passive_deletes = True)

    #user to user follower relationship
    followed = db.relationship(
        'User', secondary = 'followers',
        
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),

        # query to retrieve the followed users or followers doesnt activate until it is actually needed. 
        backref = db.backref('followers', lazy = 'dynamic'), lazy = 'dynamic')
    
    
    def follow(self, followed_user):
        self.followed.append(followed_user)

    def unfollow(self, followed_user):
        self.followed.remove(followed_user)

    def is_following(self, followed_user):
        return self.followed.filter(
            followers.c.followed_id == followed_user.id).count() > 0

    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(1000))
    content = db.Column(db.String(1000))
    date_created = db.Column(db.DateTime(timezone = True), default = func.now())
    user_of_post = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    #relationships
    comments = db.relationship('Comment', backref = 'post', passive_deletes = True)
    likes = db.relationship('Like', backref = 'post', passive_deletes = True, lazy = 'select')
    dislikes = db.relationship('Dislike', backref = 'post', passive_deletes = True, lazy = 'select')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    post_of_comment = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable = False)
    user_of_comment = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable = False)
    date_created = db.Column(db.DateTime(timezone = True), default = func.now())
    content = db.Column(db.String(1000))

    likes = db.relationship('Like', backref = 'comment', passive_deletes = True, lazy = 'select')
    dislikes = db.relationship('Dislike', backref = 'comment', passive_deletes = True, lazy = 'select')
    