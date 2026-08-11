# import asyncio
# import os
# from botpy import logging
# from botpy.ext.cog_yaml import read
# import botpy
# from botpy.message import DirectMessage, Message, C2CMessage, GroupMessage
#
# from agents.core_agent import CoreAgent
#
# config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))
# _log = logging.get_logger()
#
# class SanyueqiBot(botpy.Client):
#     async def on_ready(self):
#         _log.info(f"robot 「{self.robot.name}」 on_ready!")
#     # 好友发消息
#     async def on_c2c_message_create(self, message: C2CMessage):
#         content = message.content
#         db = PetDataStore(DB_PATH)
#         memory = ChatMemoryStore(db.conn)
#         api_key = db.get_config("api_key")
#         if not api_key:
#             return None
#         model_name = db.get_config("model_name")
#         if not model_name:
#             return None
#         base_url = db.get_config("base_url")
#         if not base_url:
#             return None
#         role = db.get_config("character_role")
#         context_limit = int(db.get_config("chat_context_limit", "10"))
#         history = memory.list_messages(limit=context_limit)
#         messages = build_chat_messages(
#             system_prompt_for_role(role),
#             history,
#             content,
#             context_limit,
#         )
#         agent = CoreAgent(
#             model=model_name,
#             api_key=api_key,
#             base_url=base_url,
#             messages=messages
#         )
#         try:
#             assistant_response = ""
#             for event in agent.run():
#                 if event["type"] == "content":
#                     assistant_response += event["content"]
#             memory.add_message("user", content, role)
#             memory.add_message("assistant", assistant_response, role)
#             await message._api.post_c2c_message(
#                 openid=message.author.user_openid,
#                 msg_type=0, msg_id=message.id,
#                 content=f"{assistant_response}"
#             )
#         finally:
#             db.close()
#     # 群内发消息
#     async def on_group_at_message_create(self, message: GroupMessage):
#         content = message.content
#         db = PetDataStore(DB_PATH)
#         memory = ChatMemoryStore(db.conn)
#         api_key = db.get_config("api_key")
#         if not api_key:
#             return None
#         model_name = db.get_config("model_name")
#         if not model_name:
#             return None
#         base_url = db.get_config("base_url")
#         if not base_url:
#             return None
#         role = db.get_config("character_role")
#         context_limit = int(db.get_config("chat_context_limit", "10"))
#         history = memory.list_messages(limit=context_limit)
#         messages = build_chat_messages(
#             system_prompt_for_role(role),
#             history,
#             content,
#             context_limit,
#         )
#         agent = CoreAgent(
#             model=model_name,
#             api_key=api_key,
#             base_url=base_url,
#             messages=messages
#         )
#         try:
#             assistant_response = ""
#             for event in agent.run():
#                 if event["type"] == "content":
#                     assistant_response += event["content"]
#             memory.add_message("user", content, role)
#             memory.add_message("assistant", assistant_response, role)
#             await message._api.post_group_message(
#                 group_openid=message.group_openid,
#                 msg_type=0,
#                 msg_id=message.id,
#                 content=f"{assistant_response}")
#         finally:
#             db.close()
#     # 机器人被at
#     # async def on_at_message_create(self, message: Message):
#     #     _log.info(message.author.avatar)
#     #     if "sleep" in message.content:
#     #         await asyncio.sleep(10)
#     #     _log.info(message.author.username)
#     #     await message.reply(content=f"机器人{self.robot.name}收到你的@消息了: {message.content}")
#
# if __name__ == "__main__":
#     # 通过预设置的类型，设置需要监听的事件通道
#     # intents = botpy.Intents.none()
#     # intents.public_guild_messages=True
#
#     # 通过kwargs，设置需要监听的事件通道
#     intents = botpy.Intents(public_messages=True, public_guild_messages=True)
#     client = SanyueqiBot(intents=intents)
#     client.run(appid=config["appid"], secret=config["secret"])