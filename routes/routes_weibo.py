from models.comment import Comment
from models.user import User
from models.weibo import Weibo
from routes import (
    redirect,
    current_user,
    html_response,
    login_required,
)
from utils import log


def weibo_owner_required(route_function):
    """
    """
    def f(request):
        log('weibo_owner_required')
        u = current_user(request)
        method = request.method
        if method == 'POST':
            weibo_id = request.form()['id']
        else:
            weibo_id = request.query['id']
        log('*** weibo_owner_required *** weibo_id <{}>'.format(weibo_id))
        w = Weibo.one(id=int(weibo_id))

        if w.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def comment_owner_required(route_function):
    def f(request):
        log('comment_owner_required')
        u = current_user(request)
        if 'id' in request.query:
            comment_id = request.query['id']
        else:
            comment_id = request.form()['id']
        c = Comment.one(id=int(comment_id))

        if c.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def comment_owner_or_weibo_owner_required(route_function):
    """
    """
    def f(request):
        log('comment_owner_or_weibo_owner_required')
        u = current_user(request)
        if 'id' in request.query:
            comment_id = request.query['id']
        else:
            comment_id = request.form()['id']
        c = Comment.one(id=int(comment_id))
        w = Weibo.one(id=c.weibo_id)

        if u.id == c.user_id or u.id == w.user_id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def index(request):
    """
    weibo 首页的路由函数
    """
    if 'id' in request.query:
        user_id = int(request.query['id'])
        u = User.one(id=user_id)
    else:
        u = current_user(request)

    weibos = Weibo.all()
    # weibos = Weibo.find_all(user_id=u.id)

    return html_response('weibo_index.html', weibos=weibos, user=u)


@login_required
def add(request):
    """
    增加新 weibo
    """
    u = current_user(request)
    form = request.form()
    Weibo.add(form, u.id)

    return redirect('/weibo/index')


@weibo_owner_required
@login_required
def delete(request):
    weibo_id = int(request.query['id'])
    Weibo.delete(weibo_id)
    # 删除微博对应的所有评论
    cs = Comment.all(weibo_id=weibo_id)
    for c in cs:
        c.delete(c.id)
    return redirect('/weibo/index')


@weibo_owner_required
@login_required
def edit(request):
    weibo_id = int(request.query['id'])
    w = Weibo.one(id=weibo_id)
    return html_response('weibo_edit.html', weibo=w)


@weibo_owner_required
@login_required
def update(request):
    """
    更新 weibo
    """
    form = request.form()
    weibo_id = int(form['id'])
    Weibo.update(weibo_id, **form)
    return redirect('/weibo/index')


@login_required
def comment_add(request):
    """
    添加评论
    """
    u = current_user(request)
    form = request.form()
    c = Comment(form)
    c.add(u.id)

    log('comment add', c, u, form)
    return redirect('/weibo/index')


@comment_owner_or_weibo_owner_required
@login_required
def comment_delete(request):
    # 删除评论
    # 判断当前用户是否有权限
    comment_id = int(request.query['id'])
    # 只有评论用户和评论所属的微博的用户都能删除评论
    Comment.delete(comment_id)
    return redirect('/weibo/index')


@comment_owner_required
@login_required
def comment_edit(request):
    comment_id = int(request.query['id'])
    c = Comment.one(id=comment_id)
    log('in the comment_edit', c)
    return html_response('comment_edit.html', comment=c)


@comment_owner_required
@login_required
def comment_update(request):
    form = request.form()
    comment_id = int(form['id'])
    Comment.update(comment_id, **form)
    return redirect('/weibo/index')


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/weibo/index': index,
        '/weibo/add': add,
        '/weibo/delete': delete,
        '/weibo/edit': edit,
        '/weibo/update': update,
        # 评论功能
        '/comment/add': comment_add,
        '/comment/delete': comment_delete,
        '/comment/edit': comment_edit,
        '/comment/update': comment_update,
    }
    return d
