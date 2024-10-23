import json
from typing import List
from huggingface_hub import InferenceClient
from fastapi import FastAPI, status, Request
from pydantic import BaseModel, Json
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os, uvicorn
import discord, asyncio

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

token = os.getenv("DISCORD")
client = InferenceClient(api_key=os.getenv("TOKEN"))
c_id = 1298667987787845727


class DiscordBot(discord.Client):
    async def on_ready(self):
        print(f"logged in as {self.user}")


bot = DiscordBot(intents=discord.Intents.default())

print(bot.get_channel(c_id))

def addToDB(obj):
    data = None
    with open("db.json", "r") as f:
        data = json.load(f)
    data["orders"].append(obj)

    with open("db.json", "w") as f:
        json.dump(data, f, indent=4)


async def orderTooJson(convo):
    inp = convo
    con = [{"role": "system", "content": "Your job is to turn a string of messages between a fast food worker and a customer into a JSON object with this format {foods: [{name: \"\", amount:int}], drinks: []} only answer with the object, do not even put it in a code block or include any message, that is very important. here is the conversation: " + str(convo)}, {"role": "user", "content": ""}]
    obj = (
        (
            client.chat.completions.create(
                model="Qwen/Qwen2.5-72B-Instruct",
                messages=con,
                temperature=0.5,
                max_tokens=1024,
                top_p=0.7,
            )
        )
            .choices[0]
            .message
    )
    js = json.loads(obj.content)
    addToDB(js)
    channel = bot.get_channel(c_id)
    await channel.send(js)


async def newAIResp(convo):
    inp = convo
    return (
        (
            client.chat.completions.create(
                model="Qwen/Qwen2.5-72B-Instruct",
                messages=inp,
                temperature=0.5,
                max_tokens=1024,
                top_p=0.7,
            )
        )
            .choices[0]
            .message
    )


async def makeAIResp(msg):
    inp = [
        {
            "role": "system",
            "content": 'You are a fast food employee, Your job is to accept orders, and convert them into a json schema like this: "{foods: [], drinks: [], others: []}", where foods is food items and other things you eat, and drinks is things you drink, others is anything else. Respond with JUST a single json object, do not surround it in a code block or anything else. Do not add any items that do not belong in a fast food menu. To make myself clear, I only want you to put all the items in one object as a list. Make sure to include a key even if it is empty, so the object always has all three keys included.',
        },
        {"role": "user", "content": msg},
    ]
    return (
        (
            client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.3",
                messages=inp,
                temperature=0.5,
                max_tokens=1024,
                top_p=0.7,
            )
        )
            .choices[0]
            .message
    )


class Order(BaseModel):
    foods: List
    drinks: List


class OrderDB(Order):
    method: str


class Message(BaseModel):
    role: str
    content: str


class AIMessages(BaseModel):
    messages: List[Message]


@app.post("/basic", status_code=status.HTTP_204_NO_CONTENT)
async def basic(order: Order):
    item = OrderDB(method="basic", **order.model_dump())
    print(item.model_dump())
    addToDB(item.model_dump())
    channel = bot.get_channel(c_id)
    await channel.send(str(item.model_dump()))

    return None


# ai assistant conversation lol
@app.post("/convo")
async def conversation(order: AIMessages):
    m = [i.model_dump() for i in order.messages]
    out = await newAIResp(m)
    c = 0
    if "yippee" in out.content.lower():
        c = 1
        await orderTooJson(m)
        # return {"message": "Your order was complted!", "cont": 1}
    return {"message": out.content, "cont": c}


@app.post("/ai")
async def ai(order):
    # out = await makeAIResp(order.message)
    # print(out)
    # data = json.load(out.content)
    # item = OrderDB(
    # method="AI", foods=data["foods"], drinks=data["drinks"], others=data["others"]
    # )

    return None  # out


@app.get("/app")
async def appHome(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@app.get("/app/ai")
async def aiUI(request: Request):
    return templates.TemplateResponse(request=request, name="ai.html")


@app.get("/app/basic")
async def basicUI(request: Request):
    return templates.TemplateResponse(request=request, name="basic.html", context={})

async def run_fastapi():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

# Main function to run both FastAPI and Discord bot concurrently
async def main():
    # Run FastAPI and Discord bot concurrently
    await asyncio.gather(
        bot.start(token),
        run_fastapi()
    )

    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())


