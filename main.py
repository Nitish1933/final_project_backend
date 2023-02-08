from fastapi import FastAPI, UploadFile, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import peewee
from peewee import *
import datetime
import pytz
import uuid
import os
from fastapi.middleware.cors import CORSMiddleware
import bcrypt


origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


IMAGE_DIR= 'images/'

timezone = pytz.timezone('Asia/Kolkata')


DATABASE = 'database.db'

database = SqliteDatabase(DATABASE)

class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    username = CharField(unique=True, primary_key=True)
    password = CharField()
    email = CharField()
    profile_pic = CharField()


class Category(BaseModel):
    name = CharField(unique=True, null=False)


class Authentication(BaseModel):
    user_id = ForeignKeyField(User, to_field='username')
    token = CharField()


class Article(BaseModel):
    title = CharField(max_length=128, null=False)
    short_description = CharField(max_length=128, null=False)
    content = TextField(null=False)
    thumbnail = CharField()
    author = ForeignKeyField(User, to_field='username', backref='author_name')
    category = ForeignKeyField(Category, to_field='name')
    number_of_likes = IntegerField(default=0)
    number_of_comments = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = DateTimeField(default=datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S"))


class Likes(BaseModel):
    user_id = ForeignKeyField(User, to_field='username')
    article_id = ForeignKeyField(Article, to_field='id')



def create_tables():
    database.connect()
    database.create_tables([User, Authentication, Article, Category, Likes], safe = True)
    database.close()


# create_tables()


# user = User.create(username='nitish', password='nitishtest', email='nitish@gmail.com', profile_pic='https://wallpapers.com/images/hd/cool-profile-pictures-red-anime-fw4wgkj905tjeujb.jpg')
# User.create(username='aryan', password='aryantest', email='aryan@gmail.com', profile_pic='https://wallpapers.com/images/hd/cool-profile-pictures-red-anime-fw4wgkj905tjeujb.jpg')
# User.create(username='roshan', password='roshantest', email='roshan@gmail.com', profile_pic='https://wallpapers.com/images/hd/cool-profile-pictures-red-anime-fw4wgkj905tjeujb.jpg')
# User.create(username='Jatin', password='jatintest', email='jatin@gmail.com',profile_pic='https://wallpapers.com/images/hd/cool-profile-pictures-red-anime-fw4wgkj905tjeujb.jpg')
# user.save()


# article=Article.create(content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book",title= "UX review presentations",short_description="How do you create compelling presentations that wow your colleagues and impress your managers?",thumbnail="dummyurl", author="nitish", category="Customer Success")
# Article.create(content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book",title= "Migrating to linear 101",short_description="Linear helps streamline software projects, sprints, tasks, and bug tracking. Here's how to get text",thumbnail="dummyurl", author="aryan", category="Software Development")
# Article.create(content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book",title= "Building your API Stack",short_description="The rise of RESTful APIs has been met by a rise in tools for creating, testing and managing them.",thumbnail="dummyurl", author="nitish", category="Software Development")
# Article.create(content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book",title= "Bill Walsh leadership lessons",short_description="Like to know the sequence of transforming a 2-14 team into a 3x Super Bowl winning Dynasty?",thumbnail="dummyurl", author="jatin", category="Leadership")
# Article.create(content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book",title= "PM mental models",short_description="Mental models are simple expressions of complex processes or relationships",thumbnail="dummyurl", author="roshan", category="Management")
# Article.create(content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book",title= "What is Wireframing?",short_description="Introduction to Wireframing and its Principles. Learn from the best in the industry",thumbnail="dummyurl", author="nitish", category="Product")
# Article.create(content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book",title= "How collaboration makes us better designers",short_description="Collaboration can make our teams stronger, and our individual designs better",thumbnail="dummyurl", author="aryan", category="Management")
# Article.create(content="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book",title= "Our top 10 Javascript frameworks to use",short_description="JavaScript frameworks make development easy with extensive features and functionalities",thumbnail="dummyurl", author="aryan", category="Software Development")


templates = Jinja2Templates('')

# @app.get('/')
# async def home(request: Request):
#     # query = User.get(User.username == 'test')
#     # image_url = 'images/' + query.profile_pic
#     # return templates.TemplateResponse('test.html', {'request': request, 'user': query, 'image_url': image_url})


@app.post("/login")
async def loginUser(request: Request):
    req = await request.json()
    username = req.get('username')
    password = req.get('password')
    with open('.env', "r") as e:
        salt = e.read()

    salt = salt.encode('utf-8')
    byte = password.encode('utf-8')
    hash_pswd = bcrypt.hashpw(byte, salt)
    query = User.select()
    for i in query:
        userPassword = i.__data__['password']
        userBytes = userPassword.encode('utf-8')
        if userBytes == hash_pswd and i.__data__['username'] == username:
            return {"message": "Logged in", "success": True}

    return {'message': 'Invalid Credentials', 'success': False}

#Sign Up API

@app.post("/register")
async def register(request: Request):
    req = await request.json()
    username = req.get('username')
    password = req.get('password')
    email = req.get('email')
    profile_pic = req.get('profile_pic')

    with open('.env', "r") as e:
        salt = e.read()
    bytes = password.encode('utf-8')
    salt = salt.encode('utf-8')
    
    hash = bcrypt.hashpw(bytes, salt)

    try:
        new_user = User.create(username=username, email=email, password=hash, profile_pic=profile_pic)
        new_user.save()
    except peewee.IntegrityError:
        return {'message': 'Username already exists', 'success': False}

    token = str(uuid.uuid4())
    Authentication.create(user_id=new_user.username, token=token)
    return {"message": "User registered", "token": token, "user": new_user, 'success': True}


@app.get('/get_articles')
async def getArticles():
    query = Article.select()
    articles = []
    for i in query:
        articles.append({'id': i.__data__['id'], 'title': i.__data__['title'], 'short_description': i.__data__['short_description'], 'content': i.__data__['content'], 'thumbnail': i.__data__['thumbnail'], 'author': i.__data__['author'], 'category': i.__data__['category'], 'created_at': i.__data__['created_at'], 'updated_at': i.__data__['updated_at']})

    return articles


@app.get("/get_article/{id}")
def getArticle(id):
    try:
        query = Article.get(Article.id == id)
        article = []
        article.append({'id': query.__data__['id'], 'title': query.__data__['title'], 'short_description': query.__data__['short_description'], 'content': query.__data__['content'], 'thumbnail': query.__data__['thumbnail'], 'author': query.__data__['author'], 'category': query.__data__['category'], 'created_at': query.__data__['created_at'], 'updated_at': query.__data__['updated_at']})
        return article
    except Article.DoesNotExist:
        return {'message': 'Article Does Not Exist'}


@app.post("/create_article")
async def createArticle(request: Request):
    req = await request.json()
    title = req.get('title')
    short_description = req.get('short_description')
    content = req.get('content')
    thumbnail = req.get('thumbnail')
    category = req.get('category')
    token = request.headers.get("Authorization")

    try:
        authentication = Authentication.get(Authentication.token == token)
        user = authentication.user_id
    except Authentication.DoesNotExist:
        return {'message': 'Invalid Token'}

    try:
        article = Article.create(author=user, title=title, content=content, category=category, short_description = short_description, thumbnail=thumbnail)
        article.save()
    except peewee.IntegrityError as e:
        return {'message': 'Error creating post'}

    return {"message": "Article successfully posted", 'article': article}


@app.put("/edit_article/{id}")
async def updateArticle(request : Request, id):
    try:
        req = await request.form()
        article = Article.get(Article.id == id)
        article.title = req.get('title')
        article.short_description = req.get('short_description')
        article.content = req.get('content')
        article.thumbnail = req.get('thumbnail')
        article.category = req.get("category")
        article.updated_at = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
        article.save()
        return article
    except Article.DoesNotExist:
        return {'message': 'Article Does Not Exist'}


@app.delete("/delete_article/{id}")
async def deleteArticle(id): 
    try:
        article = Article.get(Article.id == int(id))
        query = Article.delete().where(Article.id == int(id))
        query.execute()
        return {'status': status.HTTP_200_OK}
    except Article.DoesNotExist:
        return {'message': 'Article Does Not Exist'}


@app.get("/filter_by_category/{category}")
async def filterByCategory(category):
    if category == 'View All':
        query = Article.select()
        articles = []
        for i in query:
            articles.append({'id': i.__data__['id'], 'title': i.__data__['title'], 'short_description': i.__data__['short_description'], 'content': i.__data__['content'], 'thumbnail': i.__data__['thumbnail'], 'author': i.__data__['author'], 'category': i.__data__['category'], 'created_at': i.__data__['created_at'], 'updated_at': i.__data__['updated_at']})

        return articles

    query = Article.select().where(Article.category_id == category)
    articles = []
    if len(query) == 0:
        return {'message': 'Nothing Found'}
    for i in query:
        articles.append({'id': i.__data__['id'], 'title': i.__data__['title'], 'short_description': i.__data__['short_description'], 'content': i.__data__['content'], 'thumbnail': i.__data__['thumbnail'], 'author': i.__data__['author'], 'category': i.__data__['category'], 'created_at': i.__data__['created_at'], 'updated_at': i.__data__['updated_at']})

    return articles


@app.get("/filter/{keyword}")
async def filter(keyword):
    query = Article.select().where(Article.content.contains(keyword))
    articles = []
    if len(query) == 0:
        return {'message': 'Nothing Found'}
    for i in query:
        articles.append({'id': i.__data__['id'], 'title': i.__data__['title'], 'short_description': i.__data__['short_description'], 'content': i.__data__['content'], 'thumbnail': i.__data__['thumbnail'], 'author': i.__data__['author'], 'category': i.__data__['category'], 'created_at': i.__data__['created_at'], 'updated_at': i.__data__['updated_at']})

    return articles


@app.get("/filter_by_author/{author}")
async def filterByAuthor(author):
    query = Article.select().where(Article.author == author)
    articles = []
    if len(query) == 0:
        return {'message': 'Nothing Found'}
    for i in query:
        articles.append({'id': i.__data__['id'], 'title': i.__data__['title'], 'short_description': i.__data__['short_description'], 'content': i.__data__['content'], 'thumbnail': i.__data__['thumbnail'], 'author': i.__data__['author'], 'category': i.__data__['category'], 'created_at': i.__data__['created_at'], 'updated_at': i.__data__['updated_at']})

    return articles


@app.put('/like/{post_id}')
async def likePost(post_id):
    try:
        article = Article.get(Article.id == str(post_id))
    except Article.DoesNotExist:
        return {'message': 'Article Doesnt Exist'}
    print(article.number_of_likes)

    user_id = 'sanjuli'

    query = Likes.select().where(Likes.article_id == post_id)
    for i in query:
        if i.__data__['user_id'] == user_id:
            article.number_of_likes = article.number_of_likes - 1
            article.save()
            sub_query = Likes.delete().where(Likes.user_id == user_id)
            sub_query.execute()
            return {'message': 'Post was disliked'}

    article.number_of_likes = article.number_of_likes + 1
    article.save()
    like = Likes.create(user_id='sanjuli', article_id=post_id)
    like.save()

    return {"message": "Post was liked"}


@app.get('/likedby/{post_id}')
async def likedBy(post_id):
    query = Likes.select().where(Likes.article_id == post_id)
    users = []

    if len(query) == 0:
        return {'msg': 'no one has liked this post yet'}
    for i in query:
        users.append({'username': i.__data__['user_id']})

    return users