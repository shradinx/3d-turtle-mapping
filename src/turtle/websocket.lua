func_tbl = {
    ["handshake"] = function(ws)
        print("Handshake Established!")
        ws.send("handshake|Yes")
    end,
    ["inspect"] = function(ws)
        local exists, data = turtle.inspect()
        local msg = "inspect|" .. textutils.serialiseJSON(data)
        ws.send(msg)
    end,
    ["inspect_up"] = function(ws)
        local exists, data = turtle.inspectUp()
        local msg = "inspect_up|" .. textutils.serialiseJSON(data)
        ws.send(msg)
    end,
    ["inspect_down"] = function(ws)
        local exists, data = turtle.inspectDown()
        local msg = "inspect_down|" .. textutils.serialiseJSON(data)
        ws.send(msg)
    end,
    ["turn_left"] = function(ws)
        local turn, msg = turtle.turnLeft()
        local text = "turn_left|" .. tostring(turn)
        if msg ~= nil then
            text = text .. '|' .. msg
        end
        ws.send(text)
    end,
    ["turn_right"] = function(ws)
        local turn, msg = turtle.turnRight()
        local text = "turn_right|" .. tostring(turn)
        if msg ~= nil then
            text = text .. '|' .. msg
        end
        ws.send(text)
    end,
    ["forward"] = function(ws)
        local canMove, msg = turtle.forward()
        local text = "forward|" .. tostring(canMove)
        if msg ~= nil then
            text = text .. '|' .. msg
        end
        ws.send(text)
    end,
    ["back"] = function(ws)
        local canMove, msg = turtle.back()
        local text = "back|" .. tostring(canMove)
        if msg ~= nil then
            text = text .. '|' .. msg
        end
        ws.send(text)
    end,
    ["up"] = function(ws)
        local canMove, msg = turtle.up()
        local text = "up|" .. tostring(canMove)
        if msg ~= nil then
            text = text .. '|' .. msg
        end
        ws.send(text)
    end,
    ["down"] = function(ws)
        local canMove, msg = turtle.down()
        local text = "down|" .. tostring(canMove)
        if msg ~= nil then
            text = text .. '|' .. msg
        end
        ws.send(text)
    end,
    ["dig | True"] = function(ws)
        local isBlock, data = turtle.inspect()
        if not isBlock then
            return
        end
        local success, msg = turtle.dig()
        local text = "dig|" .. tostring(success)
        if msg ~= nil then
            text = text .. "|" .. msg
        end
        ws.send(text)
    end,
    ["dig_up | True"] = function(ws)
        local isBlock, data = turtle.inspectUp()
        if not isBlock then
            return
        end
        local success, msg = turtle.digUp()
        local text = "dig_up|" .. tostring(success)
        if msg ~= nil then
            text = text .. "|" .. msg
        end
        ws.send(text)
    end,
    ["dig_down | True"] = function(ws)
        local isBlock, data = turtle.inspectDown()
        if not isBlock then
            return
        end
        local success, msg = turtle.digDown()
        local text = "dig_down|" .. tostring(success)
        if msg ~= nil then
            text = text .. "|" .. msg
        end
        ws.send(text)
    end
}
 
local function connect()
    return http.websocket("ws://0.0.0.0:8000")
end
 
local ws = connect()
if not ws then
    print("Failed to connect websocket!")
    return
end
 
local function selectSlot(slot)
    turtle.select(slot)
end
 
local function handleInventoryChange(msg)
    for s in string.gmatch(msg, "%S+") do
        local num = tonumber(s) or -1
        if num ~= -1 then
            selectSlot(num)
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
 
while true do
    local event, url, msg, b = os.pullEvent()
 
    if event ~= "websocket_message" then
        goto continue
    end
 
    local func = func_tbl[msg]
    print(msg)
    if string.find(msg, "select_slot") then
        handleInventoryChange(msg)
    else
        if func then
            func(ws)
        end
    end
 
    ::continue::
    -- os.sleep(0.5)
end