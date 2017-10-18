from app import app

if __name__ == "__main__":
    test = input("Local (l) or LAN (t)")
    if(test == "l"):
        app.run(debug=True, use_reloader=False)
    elif(test == "t"):
        app.run(host="0.0.0.0", debug=True, use_reloader=False)
    else:
        print("Wrong input")