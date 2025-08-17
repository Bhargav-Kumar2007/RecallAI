from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from uuid import uuid4
import sqlite3
from openai import OpenAI
import dearpygui.dearpygui as dpg
import tkinter as tk
from datetime import datetime
import os
import shutil
from tkinter import filedialog
import subprocess
import sys


chrclient = chromadb.PersistentClient(path="db")
collection = chrclient.get_or_create_collection(name="chat_memory")
model = SentenceTransformer('all-MiniLM-L6-v2')
conn = sqlite3.connect("chatbot_memory.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_logs (
id TEXT PRIMARY KEY,
reply TEXT,
message TEXT,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)
conn.close()
def chunk_split(prompt,csize,csmooth):
   text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=csize,       # Maximum size of each chunk
      chunk_overlap=csmooth      # Overlap between chunks for context preservation
   )
   chunks = text_splitter.split_text(prompt)
   return chunks

def chunks_vector(chunks):
   lst=model.encode(chunks, show_progress_bar=False)
   return lst

def writedata(chunks,embeddings,who):
   collection.add(
      documents=chunks,
      embeddings=embeddings,
      ids=[str(uuid4()) for _ in chunks],
      metadatas=[{"source": who} for _ in chunks]
   )

def find_prominent(prompt,num):
   query_embedding = model.encode(prompt)
   results = collection.query(
      query_embeddings=[query_embedding],
      n_results=num
   )
   ret=str()
   for i in range(len(results['documents'])):
      """source_meta = results['metadatas'][i][0]  # Fix: grab first metadata dict
      source = source_meta.get('source', 'unknown')"""
      ret += f"{results['documents'][i]}\n"
   return ret

def rawwright(prompt,reply):
   conn = sqlite3.connect("chatbot_memory.db")
   cursor = conn.cursor()
   msg_id = str(uuid4())
   cursor.execute(
      "INSERT INTO chat_logs (id, reply, message) VALUES (?, ?, ?)",
      (msg_id, reply, prompt)
   )
   conn.commit()
   conn.close()
def rawread():
   conn = sqlite3.connect("chatbot_memory.db")
   cursor = conn.cursor()
   cursor.execute(
        "SELECT message, reply, timestamp FROM chat_logs ORDER BY timestamp ASC"
    )
   rows = cursor.fetchall()
   conn.close()
   return rows

def aigen(prompt,last_msgs,prom_msgs,temp=0.5,modelname="deepseek/deepseek-r1-0528:free"):
   final_prompt = """You are a helpful, emotionally aware, and friendly AI assistant.

Your job is to respond directly and naturally to the user's current message. You are given:
- Relevant past message snippets
- Recent chat history
- The user's new message

You do NOT need to explain your reasoning. Just respond naturally and helpfully — as if you're talking to a friend in a chat.

Prominent memory:
\"\"\""""+prom_msgs+"""\"\"\"

Recent history:
\"\"\""""+last_msgs+"""\"\"\"

User's message:
\"\"\""""+prompt+"""\"\"\"
"""
   completion = client.chat.completions.create(
   model=modelname,
   messages=[
      {
        "role": "user",
        "content": final_prompt
      }
   ],
   temperature=temp
  )
   return completion.choices[0].message.content

def mainfunc(user_input,num=100,temp=0.5, model="deepseek/deepseek-r1-0528:free",csize=320,csmooth=48,hisnum=380000):
   # Step 1: Get 100 prominent memory chunks
   conn = sqlite3.connect("chatbot_memory.db")
   cursor = conn.cursor()
   prom_msgs = find_prominent(user_input, num)

   # Step 2: Get last messages from chat_logs until ~380,000 characters total
   cursor.execute("SELECT message, reply FROM chat_logs ORDER BY timestamp DESC")
   rows = cursor.fetchall()

   total_chars = 0
   last_msgs_list = []
   for message, reply in rows:
      pair = f"User: {message}\nAI: {reply}\n"
      total_chars += len(pair)
      if total_chars > hisnum:
         break
      last_msgs_list.append(pair)
   conn.close()
   # Reverse to chronological order
   last_msgs_list.reverse()
   last_msgs = ''.join(last_msgs_list)

   # Step 3: Get AI response
   ai_response = aigen(user_input, last_msgs, prom_msgs, temp, model)
   # Step 4: Chunk the user input + AI reply together
   chunks = chunk_split(user_input,csize,csmooth)
   embeddings = chunks_vector(chunks)
   writedata(chunks, embeddings, who="User")
   # Step 5: Embed chunks
   chunks = chunk_split(ai_response,csize,csmooth)
   embeddings = chunks_vector(chunks)
   writedata(chunks, embeddings, who="ChatBot")

   # Step 7: Save raw messages into SQLite
   rawwright(user_input, ai_response)
   return ai_response


msg=rawread()

# Use tkinter to get screen resolution
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()

dpg.create_context()
dpg.create_viewport(title='RecallAI', width=screen_width, height=screen_height, small_icon="favicon(2).ico",large_icon="favicon(3).ico")
dpg.setup_dearpygui()
dpg.show_viewport()
with dpg.theme() as button_theme:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 122, 204, 255])         # Normal color
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 153, 255, 255])  # Hover color
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 102, 204, 255])   # Clicked color
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 60, 5)
with dpg.theme() as button_flat:
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, [0, 122, 204, 255])         # Normal color
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [0, 122, 204, 255])  # Hover color
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [0, 122, 204, 255])   # Clicked color
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 7)  # Rounded corners
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 60, 5)
with dpg.font_registry():
    font = dpg.add_font("C:\\Windows\\Fonts\\segoeui.ttf", 25)
count=0
def addtext(msg,user):
    global count
    tag=f"chat{count}"
    count+=1
    dpg.add_button(label=user,parent="chats",tag=tag)
    dpg.bind_item_theme(tag, button_flat)
    if count%2:
        dpg.add_text(msg,parent="chats",color= (200, 200, 255),wrap=screen_width * 0.7)
    else:
        dpg.add_text(msg,parent="chats",color= (255, 255, 255),wrap=screen_width * 0.7)
def scroll():
    dpg.set_y_scroll("chats", dpg.get_y_scroll_max("chats"))
def Send():
    ask = dpg.get_value("input")
    if len(ask)>80000 or len(ask.strip())==0:
        return 0
    dpg.set_value("input", "")
    dpg.add_text("----"+datetime.now().strftime("%Y-%m-%d %H:%M:%S"),parent="chats",color=(180, 180, 180))
    addtext(ask,"User")
    reply=mainfunc(ask,dpg.get_value("num"),dpg.get_value("temp"),dpg.get_value("model"),dpg.get_value("csize"),dpg.get_value("csmooth"),dpg.get_value("hisnum"))
    addtext(reply,"Memory Bot") 
    dpg.add_text("", parent="chats")
    dpg.set_frame_callback(2,scroll)
def refresh_chats():
    global count
    count = 0  
    for item in dpg.get_item_children("chats", 1):
        dpg.delete_item(item)
    msgs = rawread()
    if msgs:
        for msg, reply, ts in msgs:
            dpg.add_text("----"+ts,parent="chats",color=(180, 180, 180))
            addtext(msg, "User")
            addtext(reply, "Memory Bot")
            dpg.add_text("", parent="chats")
    dpg.set_frame_callback(2, scroll)
def confirm_delete():
    if dpg.does_item_exist("delete_popup"):
        dpg.delete_item("delete_popup")  # Remove if already exists

    with dpg.window(
        label="Confirm Deletion",
        modal=True,
        tag="delete_popup",
        no_collapse=True,
        no_close=True,
        width=400,
        height=200
    ):
        dpg.add_text("⚠️ WARNING: This will permanently delete ALL chats and memories.", wrap=380)
        dpg.add_text("BETTER TO CREATE A BACKUP.", wrap=380)
        dpg.add_text("This action cannot be undone.", wrap=380)
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Cancel", width=100, callback=lambda: dpg.delete_item("delete_popup"))
            dpg.add_button(label="Delete Anyway", width=150, callback=delete_chats_confirmed)
def confirm_import():
    if dpg.does_item_exist("import_popup"):
        dpg.delete_item("import_popup")  # Remove if already exists

    with dpg.window(
        label="Confirm import",
        modal=True,
        tag="import_popup",
        no_collapse=True,
        no_close=True,
        width=400,
        height=200
    ):
        dpg.add_text("⚠️ WARNING: This will permanently delete ALL chats and memories and import new.", wrap=380)
        dpg.add_text("BETTER TO CREATE A BACKUP.", wrap=380)
        dpg.add_text("This action cannot be undone.", wrap=380)
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Cancel", width=100, callback=lambda: dpg.delete_item("import_popup"))
            dpg.add_button(label="Import Anyway", width=150, callback=import_chats)
def delete_chats_confirmed():
    conn = sqlite3.connect("chatbot_memory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_logs")
    conn.commit()
    conn.close()
    collection.delete(ids=collection.get()['ids'])
    if dpg.does_item_exist("delete_popup"):
        dpg.delete_item("delete_popup")
    refresh_chats()
def export_chats():    
    export_folder = filedialog.askdirectory(title="Select Export Folder")
    if not export_folder:
        print("Export cancelled.")
        return
    try:
        if os.path.exists("chatbot_memory.db"):
            shutil.copy2("chatbot_memory.db", os.path.join(export_folder, "chatbot_memory.db"))
        else:
            print("No SQLite DB found to export.")
        if os.path.exists("db"):
            dest_db_folder = os.path.join(export_folder, "db")
            if os.path.exists(dest_db_folder):
                shutil.rmtree(dest_db_folder)  # remove old export
            shutil.copytree("db", dest_db_folder)
        else:
            print("No ChromaDB folder found to export.")
        print(f"Chats exported to '{export_folder}'")
    except Exception as e:
        print(f"Export failed: {e}")

def import_chats():
     global chrclient, collection
     chrclient = None
     collection = None
     del chrclient
     del collection
     import gc
     gc.collect()
     dpg.stop_dearpygui()
     helper_path = os.path.join(os.path.dirname(__file__), "importhelp.py")
     subprocess.Popen([sys.executable, helper_path])
     os._exit(0)

def set_default():
    dpg.set_value("num",100)
    dpg.set_value("temp",0.5)
    dpg.set_value("model","deepseek/deepseek-r1-0528:free")
    dpg.set_value("csize",320)
    dpg.set_value("csmooth",48)
    dpg.set_value("hisnum",380000)

with dpg.window(tag="MainWindow", no_title_bar=True, no_resize=True, no_move=True,no_scrollbar=True, no_collapse=True, autosize=False,width=screen_width, height=screen_height, pos=(0, 0)):
    with dpg.group(horizontal=True):
        with dpg.child_window(tag="chats",width=screen_width*4//5-23, height=screen_height*7//10):
            pass
        with dpg.child_window(width=screen_width//5, height=screen_height*8.5//10):
            
            dpg.add_button(label="Reset Settings",width=screen_width // 6,callback=set_default)
            
            dpg.add_separator()
            dpg.add_text("Important content settings-")
            dpg.add_separator()

            dpg.add_text("Number of prominent message chunk", wrap=screen_width * 0.25)
            dpg.add_input_int(width=screen_width // 6, tag="num", default_value=100)
            dpg.add_text()
            
            dpg.add_text("Chunk Size for Memory Embedding", wrap=screen_width * 0.25)
            dpg.add_input_int(width=screen_width // 6, tag="csize", default_value=320)
            dpg.add_text()
            
            dpg.add_text("Chunk Overlap for Smooth Context", wrap=screen_width * 0.25)
            dpg.add_input_int(width=screen_width // 6, tag="csmooth", default_value=48)
            dpg.add_text()

            dpg.add_separator()
            dpg.add_text("History Chats settings-")
            dpg.add_separator()

            dpg.add_text("Max length of chat history", wrap=screen_width * 0.25)
            dpg.add_input_int(width=screen_width // 6, tag="hisnum", default_value=380000)
            dpg.add_text()

            dpg.add_separator()
            dpg.add_text("Text Generation settings-")
            dpg.add_separator()

            dpg.add_text("Choose AI Model", wrap=screen_width * 0.25)
            dpg.add_combo(
               items=["deepseek/deepseek-r1-0528:free", "openchat/openchat-3.5-1210", "mistralai/mixtral-8x7b"],
               default_value="deepseek/deepseek-r1-0528:free",
               tag="model",
               width=screen_width // 6
            )
            dpg.add_text()

            dpg.add_text("Temperature of AI Generation", wrap=screen_width * 0.25)
            dpg.add_slider_float(width=screen_width // 6, tag="temp", default_value=0.5, min_value=0.0, max_value=1.0)
            dpg.add_text()

            dpg.add_separator()
            dpg.add_text("General Chats settings-")
            dpg.add_separator()
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="EXPORT CHATS",width=screen_width // 12,callback=export_chats)
                dpg.add_button(label="IMPORT CHATS",width=screen_width // 12,callback=confirm_import)
            with dpg.group(horizontal=True):
                dpg.add_button(label="DELETE CHATS",width=screen_width // 12,callback=confirm_delete)
                dpg.add_button(label="REFRESH CHATS",width=screen_width // 12,callback=refresh_chats)
    dpg.add_input_text(tag="input",multiline=True,pos=(10,screen_height*7.2//10),width=screen_width*3.3//5,height=screen_height*1.3//10)
    dpg.add_button(tag="send_btn",label="SEND",pos=(screen_width*6.75//10,screen_height*7.2//10), callback=Send)
    dpg.bind_item_theme("send_btn", button_theme)
    dpg.bind_item_font("send_btn", font)
    
if len(msg)!=0 and count==0:
    for i in msg:
        dpg.add_text("----"+i[2],parent="chats",color=(180, 180, 180))
        addtext(i[0],"user")
        addtext(i[1],"Memory Bot")
        dpg.add_text("", parent="chats")
dpg.set_frame_callback(2,scroll)
dpg.set_primary_window("MainWindow", True)
dpg.start_dearpygui()
dpg.destroy_context()
print(screen_width,screen_height)