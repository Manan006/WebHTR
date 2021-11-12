from aioflask import Flask, render_template
import aioflask as flask
import os
import random
import asyncio
import aiosqlite
import aiohttp
from flask.wrappers import Response
import multiprocessing
import model_web
import time
import nest_asyncio
nest_asyncio.apply()


abspath = os.path.abspath(os.getcwd())
path = os.path.join(abspath,"img/line.png")
args = {
    "mode":"infer",
    "decoder":"bestpath",
    "batch_size":100,
    "fast":True,
    "line_mode":False,
    "img_file":os.path.join(abspath,"data/word.png"),
    "early_stopping":25,
    "dump":False
}
    


async def model_main(args):
    randint=random.randint(-2147483647,2147483647)
    args["randint"]=randint
    async with aiohttp.ClientSession() as session:
        model_web_url = 'http://0.0.0.0:4201/queue_img'
        async with session.post(model_web_url,data=args) as resp:
            return await resp.text()
            

async def process_img(filename):
    db = await aiosqlite.connect("img.db")
    cursor = await db.execute("SELECT `text`,`chance` FROM `img` WHERE `filename`=?",(filename,))
    data=await cursor.fetchone()
    if data==None:
        pass
    else:
        while True:
            cursor = await db.execute("SELECT `text`,`chance` FROM `img` WHERE `filename`=?",(filename,))
            data=await cursor.fetchone()
            if data[1]==0:
                await asyncio.sleep(1)
            else:
                break
        await db.close()
        return data
    await db.execute("INSERT INTO `img` (`filename`,`text`,`chance`) VALUES (?,?,?)",(filename,None,0))
    await db.commit()
    args["img_file"]=os.path.join(abspath,"img/",filename)
    # await db.close()
    # db = await aiosqlite.connect("img.db")
    randint = await model_main(args=args)
    while True:
        cursor = await db.execute("SELECT `text`,`chance` FROM `shared` WHERE `id`=?",(int(randint),))
        data=await cursor.fetchone()
        if data==None:
            await asyncio.sleep(1)
        else:
            break
    cursor = await db.execute("SELECT `text`,`chance` FROM `shared` WHERE `id`=?",(randint,))
    await db.execute("DELETE FROM `shared` WHERE `id`=?",(randint,))
    await db.commit()
    text,chance=await cursor.fetchone()
    await db.execute("DELETE FROM `img` WHERE `filename`=?",(filename,))
    await db.execute("INSERT INTO `img` (`filename`,`text`,`chance`) VALUES (?,?,?)",(filename,text,chance))
    await db.commit()
    await db.close()
    return (text,chance)

async def main():
    db = await aiosqlite.connect("img.db")
    await db.execute("""CREATE TABLE IF NOT EXISTS `img` (
    `filename` VARCHAR(300),
    `text` VARCHAR(999999999999999),
    `chance` `float(2)`);""")
    await db.execute("""CREATE TABLE IF NOT EXISTS `shared` (
    `id` INT,
    `text` VARCHAR(999999999999999),
    `chance` `float(10)`);""")
    await db.execute("DELETE FROM `img`")
    await db.execute("DELETE FROM `shared`")
    await db.commit()
    asyncio.create_task(db.close())

    app.run(host='0.0.0.0',port=6901,debug=False)

app = Flask(__name__)

@app.route("/")
async def index():
    return await render_template("bs.html")

@app.route("/read_handwriting", methods=['POST'])
async def sumbit_img():
    request=flask.request
    file = request.files['image']
    if len(file_extention:=os.path.splitext(file.filename)[-1])<=1:
        return "Invalid file"
    filename=str(random.randint(-2147483647,2147483647))+file_extention
    file.save(os.path.join(abspath,"img/",filename))
    await asyncio.sleep(0.2)
    return flask.redirect("/view/"+filename)

@app.route("/view/<filename>")
async def view_text(filename):
    text,chance=await process_img(filename)
    return await flask.render_template("bs.html",text=text,chance=chance)
    




if __name__=="__main__":
    multiprocessing.Process(target=model_web.main,args=[]).start()
    
    asyncio.run(main())
    
    while True:
        time.sleep(1)






## TODO - check the db in process_img before processing the img
## TODO - make sure all db.execute have db.commit
## TODO - add the app.routes for the images