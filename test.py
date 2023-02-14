from revChatGPT.V2 import Chatbot

async def main():
    chatbot = Chatbot(email="gogailinxichong@gmail.com", password="wk830725")
    async for line in chatbot.ask("Hello"):
        print(line["choices"][0]["text"].replace("<|im_end|>", ""), end="", flush = True)
    print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())