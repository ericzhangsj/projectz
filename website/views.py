from flask import  Blueprint, render_template, request, flash, url_for, redirect
from flask_login import current_user, login_required
from .models import Post, User, Comment, Like, Dislike, followers
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def overview():
    return render_template('overview.html', user = current_user)

@views.route('/home')
def home():
    posts = Post.query.order_by(Post.date_created.desc()).all()
    return render_template('home.html', user = current_user, posts = posts)

@views.route('/explore')
def explore():
    posts = Post.query.all()
    return render_template('explore.html', user = current_user, posts = posts)

@views.route('/create-post', methods = ['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        new_post = Post(title = title, content = content, user_of_post = current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Post has been created!')
        return redirect(url_for('views.home'))

    return render_template('create_post.html', user = current_user)

@views.route('/delete-post/<id>')
@login_required
def delete_post(id):
    post = Post.query.filter_by(id = id).first()
    
    if not post:
        flash('Post does not exist!', 'danger')
    else:
        db.session.delete(post)
        for comment in post.comments:
            db.session.delete(comment)
        for like in post.likes:
            db.session.delete(like)
        for dislike in post.dislikes:
            db.session.delete(dislike)
        db.session.commit()
        flash('Post has been deleted!', 'success')
        
    return redirect(url_for('views.home'))



@views.route('/<username>')
def user_page(username):
    user = User.query.filter_by(username = username).first()
    posts = Post.query.filter_by(user_of_post = user.id).all()
    follower_count = user.followers.count()
    followed_count = user.followed.count()
    return render_template('user_page.html', user = current_user, posts = posts, user_page = user)


@views.route('/comments/<id>', methods = ['GET', 'POST'])
def create_comment(id):
    post = Post.query.filter_by(id = id).first()
    if not post:
        flash('Post does not exist!', 'error')
    if request.method == 'POST':
        content = request.form.get('content')
        comment = Comment(content = content, post_of_comment = id, user_of_comment = current_user.id)
        db.session.add(comment)
        db.session.commit()


    return render_template('comments.html', user = current_user, post = post)

@views.route('/delete-comment/<id>')
@login_required
def delete_comment(id):
    comment = Comment.query.filter_by(id = id).first()
    post_id = comment.post.id
    
    if not comment:
        flash('Comment does not exist!', 'danger')
    else:
        for like in comment.likes:
            db.session.delete(like)
        db.session.delete(comment)
        db.session.commit()
        flash('Comment has been deleted!', 'success')
        
    return redirect(url_for('views.create_comment', id = post_id))


@views.route('/like-post/<post_id>', methods = ['GET'])
@login_required
def like_post(post_id):
    post = Post.query.filter_by(id = post_id).first()
    like = Like.query.filter_by(user_of_like = current_user.id, post_of_like = post_id).first()
    dislike = Dislike.query.filter_by(post_of_dislike = post_id, user_of_dislike = current_user.id).first()
    
    user_id = current_user.id

    if not post:
        flash('Post does not exist!')
    elif like:
        db.session.delete(like)
        db.session.commit()

        referrer = request.referrer
        if referrer.endswith('/home'):
            return redirect(url_for('views.home'))
        else:
            return redirect(url_for('views.create_comment', id = post_id))
    
    else:
        if dislike: 
             db.session.delete(dislike)
        like_new = Like(post_of_like = post_id, user_of_like = user_id)
        db.session.add(like_new)
        db.session.commit()

        referrer = request.referrer
        if referrer.endswith('/home'):
            return redirect(url_for('views.home'))
        else:
            return redirect(url_for('views.create_comment', id = post_id))
    
@views.route('/dislike-post/<post_id>', methods = ['GET'])
def dislike_post(post_id):
    post = Post.query.filter_by(id = post_id).first()
    dislike = Dislike.query.filter_by(post_of_dislike = post_id, user_of_dislike = current_user.id).first()
    like = Like.query.filter_by(user_of_like = current_user.id, post_of_like = post_id).first()
    
    if not post:
        flash('Post not found!')
    if dislike:
        db.session.delete(dislike)
        db.session.commit()

        referrer = request.referrer
        if referrer.endswith('/home'):
            return redirect(url_for('views.home'))
        else:
            return redirect(url_for('views.create_comment', id = post_id))
        
    elif not dislike:
        if like: 
             db.session.delete(like)
        dislike_new = Dislike(post_of_dislike = post_id, user_of_dislike = current_user.id)
        db.session.add(dislike_new)
        db.session.commit()

        referrer = request.referrer
        if referrer.endswith('/home'):
            return redirect(url_for('views.home'))
        else:
            return redirect(url_for('views.create_comment', id = post_id))
        

@views.route('/like-comment/<comment_id>', methods = ['GET'])
def like_comment(comment_id):
    comment = Comment.query.filter_by(id = comment_id).first()
    post = Post.query.filter_by(id = comment.post.id). first()
    liked = Like.query.filter_by(comment_of_like = comment_id, user_of_like = current_user.id).first()
    
    if not comment:
        flash('Comment does not exist!')
    elif liked:
        db.session.delete(liked)
        db.session.commit()
        return redirect(url_for('views.create_comment', id = post.id))
    else:
        new_like = Like(user_of_like = current_user.id, comment_of_like = comment_id)
        db.session.add(new_like)
        db.session.commit()
        return redirect(url_for('views.create_comment', id = post.id))



        

@views.route('/follow/<username>')
def follow_user(username):
    followed_user = User.query.filter_by(username = username).first()
    if not followed_user:
        flash('User does not exists!', 'error')
        return redirect(url_for('views.user_page', username = username))
    elif followed_user == current_user:
        flash('You cannot follow yourself!', 'error')
        return redirect(url_for('views.user_page', username = username))
    else:
        if current_user.is_following(followed_user):
            current_user.unfollow(followed_user)
            flash(f'Unfollowed {followed_user.username}!')
        else:
            current_user.follow(followed_user)
            flash(f'Followed {followed_user.username}!')
            print(follower for follower in current_user.followed)
        db.session.commit()
        return redirect(url_for('views.user_page', username = username))
        