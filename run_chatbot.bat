@echo off

cd /d "D:\venv\chatbot\Scripts"
call activate

cd /d "D:\code\250510_chatbot_langchain"
gradio chatbot.py

cmd /k
