action_tbl = {
    ["inspect"] = turtle.inspect,
    ["inspect_up"] = turtle.inspectUp,
    ["inspect_down"] = turtle.inspectDown,
    ["dig"] = { turtle.inspect, turtle.dig },
    ["dig_up"] = { turtle.inspectUp, turtle.digUp },
    ["dig_down"] = { turtle.inspectDown, turtle.digDown },
    ["forward"] = turtle.forward,
    ["back"] = turtle.back,
    ["up"] = turtle.up,
    ["down"] = turtle.down,
    ["turn_left"] = turtle.turnLeft,
    ["turn_right"] = turtle.turnRight,
    ["place"] = turtle.place,
    ["place_up"] = turtle.placeUp,
    ["place_down"] = turtle.placeDown
}

local function concatMessage(text, msg)
    if msg == nil then
        return text
    end
    return text .. "|" .. msg
end

local function inspectAction(ws, direction)
    local func = action_tbl[direction]
    local exists, data = func()
    local msg = direction .. "|" .. textutils.serialiseJSON(data)
    ws.send(msg)
end

local function inspectForward(ws)
    inspectAction(ws, "inspect")
end

local function inspectDown(ws)
    inspectAction(ws, "inspect_down")
end

local function inspectUp(ws)
    inspectAction(ws, "inspect_up")
end

local function turnAction(ws, direction)
    local func = action_tbl[direction]
    local turn, msg = func()
    local text = direction .. "|" .. tostring(turn)
    ws.send(concatMessage(text, msg))
end

local function turnLeftAction(ws)
    turnAction(ws, "turn_left")
end

local function turnRightAction(ws)
    turnAction(ws, "turn_right")
end

local function moveAction(ws, direction)
    local func = action_tbl[direction]
    local canMove, msg = func()
    local text = direction .. "|" .. tostring(canMove)
    ws.send(concatMessage(text, msg))
end

local function moveForward(ws)
    moveAction(ws, "forward")
end

local function moveBack(ws)
    moveAction(ws, "back")
end

local function moveUp(ws)
    moveAction(ws, "up")
end

local function moveDown(ws)
    moveAction(ws, "down")
end

local function digAction(ws, direction)
    local funcs = action_tbl[direction]
    local isBlock, data = funcs[1]()
    if not isBlock then
        return
    end
    local success, msg = funcs[2]()
    local text = direction .. "|" .. tostring(success)
    ws.send(concatMessage(text, msg))
end

local function digDownAction(ws)
    digAction(ws, "dig_down")
end

local function digUpAction(ws)
    digAction(ws, "dig_up")
end

local function digForwardAction(ws)
    digAction(ws, "dig")
end

local function placeAction(ws, direction)
    local func = action_tbl[direction]
    local detail = turtle.getItemDetail()
    local placed, msg = func()
    if detail == nil then
        detail = {}
    end
    local text = direction .. "|" .. textutils.serialiseJSON(detail)
    ws.send(concatMessage(text, msg))
end

local function placeDownAction(ws)
    placeAction(ws, "place_down")
end

local function placeUpAction(ws)
    placeAction(ws, "place_up")
end

local function placeForwardAction(ws)
    placeAction(ws, "place")
end

func_tbl = {
    ["handshake"] = function(ws)
        print("Handshake Established!")
        ws.send("handshake|Yes")
    end,
    ["inspect"] = function(ws)
        inspectForward(ws)
    end,
    ["inspect_up"] = function(ws)
        inspectUp(ws)
    end,
    ["inspect_down"] = function(ws)
        inspectDown(ws)
    end,
    ["turn_left"] = function(ws)
        turnLeftAction(ws)
    end,
    ["turn_right"] = function(ws)
        turnRightAction(ws)
    end,
    ["forward"] = function(ws)
        moveForward(ws)
    end,
    ["back"] = function(ws)
        moveBack(ws)
    end,
    ["up"] = function(ws)
        moveUp(ws)
    end,
    ["down"] = function(ws)
        moveDown(ws)
    end,
    ["dig | True"] = function(ws)
        digForwardAction(ws)
    end,
    ["dig_up | True"] = function(ws)
        digUpAction(ws)
    end,
    ["dig_down | True"] = function(ws)
        digDownAction(ws)
    end,
    ["place"] = function(ws)
        placeForwardAction(ws)
    end,
    ["place_up"] = function(ws)
        placeUpAction(ws)
    end,
    ["place_down"] = function(ws)
        placeDownAction(ws)
    end,
}

local function handleInventoryChange(ws, msg)
    for s in string.gmatch(msg, "%S+") do
        local num = tonumber(s) or -1
        if num ~= nil and num ~= -1 then
            print(num)
            turtle.select(num)
            break
        end
    end

    detail = turtle.getItemDetail()
    text = "select_slot|"

    if detail ~= nil then
        text = text .. textutils.serialiseJSON(detail)
    else
        text = text .. "Empty"
    end

    ws.send(text)
end

local ws, err = http.websocket("ws://0.0.0.0:8000")
if err then
    print(err)
    return
end

local function fetch(ws)
    return 
end

term.clear()
term.setCursorPos(1, 1)
print("   PyTurtle OS {o_o}\n")

while true do
    local msg = ws.receive()

    if msg == nil then
        print("Failed to fetch...")
        os.sleep(5)
        goto continue
    end

    print(msg)

    local func = func_tbl[msg]

    if string.find(msg, "select_slot") then
        handleInventoryChange(ws, msg)
    else
        if func then
            func(ws)
        end
    end

    ::continue::
end

ws.close()
