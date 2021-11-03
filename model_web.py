from flask import Flask, render_template
import flask as flask
import sqlite3
import multiprocessing
import random

from main import model_main

app = Flask(__name__)
processes=[]

@app.route("/queue_img",methods=["POST"])
def execute():
    obj=flask.request.form
    args = {
    "mode":obj["mode"],
    "decoder":obj["decoder"],
    "batch_size":obj["batch_size"],
    "fast":obj["fast"],
    "line_mode":obj["line_mode"],
    "img_file":obj["img_file"],
    "early_stopping":obj["early_stopping"],
    "dump":obj["dump"]
}
    randint=random.randint(-2147483647,2147483647)
    args["randint"]=randint
    process=multiprocessing.Process(target=model_main,args=[args])
    process.start()
    return str(randint)

def model_main(args):
    import model_src.main as model
    result=model.main(args)
    db = sqlite3.connect("img.db")
    db.execute("INSERT INTO `shared` (`id`,`text`,`chance`) VALUES (?,?,?)",(args["randint"],result["Recognized"],round(result["Probability"],2)))
    db.commit()
    db.close()

def main():
    app.run(host='0.0.0.0',debug=True,port=6000)

if __name__=="__main__":
    main()