import pymongo
from pymongo import MongoClient
import datetime
import pprint

# making a connection with MongoClient
# if we don't pass it argument, it will connect on default host and port
client = MongoClient('localhost', 27017)

# Getting a database
db = client.test_database

# Getting a collection 
collection = db.test_collection

# Create a document
post = {"author": "Mike",
        "text": "My first blog post!",
        "tags": ["mongodb", "python", "pymongo"],
        "date": datetime.datetime.utcnow()}

# inserting  a document
posts = db.posts
post_id = posts.insert_one(post).inserted_id # inserted_id gives us inserted id of this document
db.list_collection_names() # gives us the names of collenctions in the database

# Getting a single document with find_one()
pprint.pprint(posts.find_one()) 
pprint.pprint(posts.find_one({"author": "Mike"})) # gives the post whose name is Mike
pprint.pprint(posts.find_one({"author": "Eliot"}))  # gives the post whose name is Mike

# Bulk inserts
# we put two documents in new_posts
new_posts = [{"author": "Mike",
              "text": "Another post!",
               "tags": ["bulk", "insert"],
               "date": datetime.datetime(2009, 11, 12, 11, 14)},
              {"author": "Eliot",
               "title": "MongoDB is fun",
               "text": "and pretty easy too!",
               "date": datetime.datetime(2009, 11, 10, 10, 45)}]

# add this document to the collection whose name is posts
result = posts.insert_many(new_posts)

result.inserted_ids # return inserted id

# Querying for more than one document
# posts.find() is iterabel object

for post in posts.find():
    pprint.pprint(post)

for post in posts.find({"author": "Mike"}):
    pprint.pprint(post)

# counting
posts.count_documents({})
posts.count_documents({"author": "Mike"})