from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.template import loader
import pymongo


mongo_url = getattr(settings, "MONGO_URL", None)
mongo_db = getattr(settings, "MONGO_DB", None)

mongo_client = pymongo.MongoClient(mongo_url)
db = mongo_client[mongo_db]
mongo_collection = db['news_spider']

# Create your views here.
def index(request):
    template = loader.get_template("news/index.html")
    news = mongo_collection.find({}).sort({created: -1}).limit(5)
    context = {"news": news}
    return render(request, "news/index.html", context)
