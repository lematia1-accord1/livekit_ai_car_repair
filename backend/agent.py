# from __future__ import annotations
# from livekit.agents import (
#     AutoSubscribe,
#     JobContext,
#     WorkerOptions,
#     cli,
#     llm
# )
# #from livekit.agents.multimodal import MultimodalAgent
# from livekit.agents import Worker, JobContext, AutoSubscribe

# from livekit.plugins import openai
# from dotenv import load_dotenv
# from api import AssistantFnc
# from prompts import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_VIN_MESSAGE
# import os

# load_dotenv()

# async def entrypoint(ctx: JobContext):
#     await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
#     await ctx.wait_for_participant()
    
#     model = openai.realtime.RealtimeModel(
#         instructions=INSTRUCTIONS,
#         voice="shimmer",
#         temperature=0.8,
#         modalities=["audio", "text"]
#     )
#     assistant_fnc = AssistantFnc()
#     assistant = MultimodalAgent(model=model, fnc_ctx=assistant_fnc)
#     assistant.start(ctx.room)
    
#     session = model.sessions[0]
#     session.conversation.item.create(
#         llm.ChatMessage(
#             role="assistant",
#             content=WELCOME_MESSAGE
#         )
#     )
#     session.response.create()
    
#     @session.on("user_speech_committed")
#     def on_user_speech_committed(msg: llm.ChatMessage):
#         if isinstance(msg.content, list):
#             msg.content = "\n".join("[image]" if isinstance(x, llm.ChatImage) else x for x in msg)
            
#         if assistant_fnc.has_car():
#             handle_query(msg)
#         else:
#             find_profile(msg)
        
#     def find_profile(msg: llm.ChatMessage):
#         session.conversation.item.create(
#             llm.ChatMessage(
#                 role="system",
#                 content=LOOKUP_VIN_MESSAGE(msg)
#             )
#         )
#         session.response.create()
        
#     def handle_query(msg: llm.ChatMessage):
#         session.conversation.item.create(
#             llm.ChatMessage(
#                 role="user",
#                 content=msg.content
#             )
#         )
#         session.response.create()
    
# if __name__ == "__main__":
#     cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

from livekit.agents import Worker, JobContext, AutoSubscribe
from livekit.plugins import openai
from api import AssistantFnc
from prompts import WELCOME_MESSAGE, INSTRUCTIONS, LOOKUP_VIN_MESSAGE
import asyncio

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()

    assistant_fnc = AssistantFnc()

    # Initialize RealtimeModel (from livekit.plugins.openai)
    model = openai.realtime.RealtimeModel(
        model="gpt-4o-realtime-preview",
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"]
    )

    # Print system instructions and welcome
    print(f"Assistant (system instructions): {INSTRUCTIONS}")
    print(f"Assistant (welcome): {WELCOME_MESSAGE}")

    # Example of handling messages
    async def on_message(msg):
        content = getattr(msg, "content", msg)
        if isinstance(content, list):
            content = "\n".join(
                getattr(x, "text", "[audio]" if hasattr(x, "url") else str(x))
                for x in content
            )
        elif not isinstance(content, str):
            content = str(content)

        if assistant_fnc.has_car():
            response_text = assistant_fnc.handle_query(content)
        else:
            response_text = assistant_fnc.lookup_vin(content)

        if response_text:
            print(f"Assistant: {response_text}")
            # Send to participants if your model supports it
            model.send({"type": "input_text", "text": response_text})

    # Bind the handler to model events
    model.on("message", on_message)

    # Keep loop running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    from livekit.agents import cli, WorkerOptions
    from dotenv import load_dotenv
    load_dotenv("sample.env")

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            url="YOUR_LIVEKIT_URL",
            api_key="YOUR_LIVEKIT_API_KEY",
            api_secret="YOUR_LIVEKIT_API_SECRET"
        )
    )
