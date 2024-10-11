from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from frameutils import Bluetooth
import asyncio
import traceback
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Simulated database
orders = []

# Global Bluetooth connection and event loop
bluetooth = Bluetooth()
loop = asyncio.new_event_loop()

def run_in_loop(coro):
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        customer = request.form.get('customer')
        order = request.form.get('order')
        dietary_restrictions = request.form.get('dietary_restrictions')

        orders.append({
            'customer': customer,
            'order': order,
            'dietary_restrictions': dietary_restrictions
        })

        # Display the order on Frame glasses
        socketio.start_background_task(display_on_frame, f"New order: {order} for {customer}")

        return jsonify({"status": "success", "message": "Order added"})

    return render_template('index.html', orders=orders)

@socketio.on('display_message')
def handle_display_message(data):
    print(f"Received message to display: {data}")
    socketio.start_background_task(display_on_frame_wrapper, data)
    return {"status": "success", "message": "Displaying message"}

async def display_on_frame(data):
    try:
        print(f"Starting display_on_frame with data: {data}")
        if not bluetooth.is_connected():
            print("Bluetooth not connected. Attempting to connect...")
            connected = await bluetooth.connect()
            if not connected:
                print("Failed to connect to Frame glasses")
                return

        print(f"Preparing Lua commands to display text: {data['text']}")
        
        # Set brightness
        await bluetooth.send_lua(f"frame.display.set_brightness({data['brightness']})")
        
        # Clear the screen
        await bluetooth.send_lua("frame.display.clear()")
        
        # Calculate position
        x, y = calculate_position(data['position'])
        
        # Display text with color and position
        lua_command = f"frame.display.text('{data['text']}', {x}, {y}, {{color='{data['color']}', align='center', valign='center'}})"
        print(f"Sending Lua command: {lua_command}")
        result = await bluetooth.send_lua(lua_command)
        
        # Show the display
        await bluetooth.send_lua("frame.display.show()")
        print(f"Display result: {result}")

        await asyncio.sleep(5)

        print("Preparing clear screen command")
        await bluetooth.send_lua("frame.display.clear()")
        await bluetooth.send_lua("frame.display.show()")
        print("Screen cleared")

    except Exception as e:
        print(f"An error occurred in display_on_frame: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())

    finally:
        print("Finished display_on_frame function")

def calculate_position(position):
    screen_width = 564
    screen_height = 364
    positions = {
        'top-left': (10, 10),
        'top-center': (screen_width // 2, 10),
        'top-right': (screen_width - 10, 10),
        'center-left': (10, screen_height // 2),
        'center': (screen_width // 2, screen_height // 2),
        'center-right': (screen_width - 10, screen_height // 2),
        'bottom-left': (10, screen_height - 10),
        'bottom-center': (screen_width // 2, screen_height - 10),
        'bottom-right': (screen_width - 10, screen_height - 10),
    }
    return positions.get(position, positions['center'])

def display_on_frame_wrapper(data):
    run_in_loop(display_on_frame(data))

def run_event_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

if __name__ == '__main__':
    # Start the event loop in a separate thread
    Thread(target=run_event_loop, daemon=True).start()

    socketio.run(app, debug=True)