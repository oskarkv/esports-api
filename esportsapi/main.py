from flask import Flask, request, jsonify
import graphene as g
import sys
from . import graphql
from . import db_functions as db

if len(sys.argv) == 1 or sys.argv[1] not in ["app", "db"]:
    print('Please give the argument `app` to run the "app API",' +
          '\nor `db` to run the "database API".')
    sys.exit(1)
elif sys.argv[1] == "app":
    schema = g.Schema(query=graphql.Query)
else:
    schema = g.Schema(query=graphql.Query, mutation=graphql.Mutation)

# Get a fresh database on every restart to test more easily.
# Obviously this wouldn't work in a real app.
db.recreate_db()
db.load_example_data()

app = Flask(__name__)

http_bad_request = 400

@app.route("/")
def index():
    result = schema.execute(request.args.get("query"))
    if result.errors:
        return jsonify({"error": str(result.errors)}), http_bad_request
    else:
        return jsonify(result.data)

if __name__ == "__main__":
    app.run(debug=True)
