-- Civ 5 AI Bridge - State Exporter (Super Spy Mode)
-- Dumps extreme tactical game state to Lua.log every turn.

print("CIV5_AI_BRIDGE: Mod Loaded")

function EscapeString(str)
    if str == nil then return "" end
    str = string.gsub(str, '\\', '\\\\')
    str = string.gsub(str, '"', '\\"')
    str = string.gsub(str, '\n', '\\n')
    str = string.gsub(str, '\r', '\\r')
    return str
end

function DumpGameState()
    local turn = Game.GetGameTurn()
    local activePlayerID = Game.GetActivePlayer()
    
    -- Build Resource Dictionary
    local resDict = {}
    for res in GameInfo.Resources() do
        local name = res.Type or "Unknown"
        table.insert(resDict, '"' .. res.ID .. '":"' .. EscapeString(name) .. '"')
    end
    
    -- Build Improvement Dictionary
    local impDict = {}
    for imp in GameInfo.Improvements() do
        local name = imp.Type or "Unknown"
        table.insert(impDict, '"' .. imp.ID .. '":"' .. EscapeString(name) .. '"')
    end
    
    local featDict = {}
    for f in GameInfo.Features() do
        local name = f.Type or "Unknown"
        table.insert(featDict, '"' .. f.ID .. '":"' .. EscapeString(name) .. '"')
    end

    local data = {}
    
    local firstPlayer = true
    for i = 0, GameDefines.MAX_CIV_PLAYERS-1, 1 do
        local pPlayer = Players[i]
        if pPlayer and pPlayer:IsAlive() then
            if not firstPlayer then table.insert(data, ",") end
            firstPlayer = false
            
            local pName = EscapeString(pPlayer:GetName())
            local cName = EscapeString(pPlayer:GetCivilizationShortDescription())
            
            -- Super Spy Diplomacy (Hidden Approach)
            local diplomacy = "Unknown"
            if not pPlayer:IsMinorCiv() and not pPlayer:IsBarbarian() and i ~= activePlayerID then
                pcall(function()
                    local approach = pPlayer:GetApproachTowardsUsGuess(activePlayerID)
                    if approach == MajorCivApproachTypes.MAJOR_CIV_APPROACH_HOSTILE then diplomacy = "Hostile"
                    elseif approach == MajorCivApproachTypes.MAJOR_CIV_APPROACH_DECEPTIVE then diplomacy = "Deceptive (Planning Attack!)"
                    elseif approach == MajorCivApproachTypes.MAJOR_CIV_APPROACH_GUARDED then diplomacy = "Guarded"
                    elseif approach == MajorCivApproachTypes.MAJOR_CIV_APPROACH_AFRAID then diplomacy = "Afraid"
                    elseif approach == MajorCivApproachTypes.MAJOR_CIV_APPROACH_FRIENDLY then diplomacy = "Friendly"
                    elseif approach == MajorCivApproachTypes.MAJOR_CIV_APPROACH_NEUTRAL then diplomacy = "Neutral"
                    end
                end)
            elseif pPlayer:IsMinorCiv() then
                pcall(function()
                    local friendLvl = pPlayer:GetMinorCivFriendshipLevelWithMajor(activePlayerID)
                    if friendLvl == 0 then diplomacy = "Neutral"
                    elseif friendLvl == 1 then diplomacy = "Friends"
                    elseif friendLvl == 2 then diplomacy = "Allies"
                    else diplomacy = "Angry" end
                end)
            end
            
            local sciPerTurn = 0
            local culPerTurn = 0
            local goldPerTurn = 0
            pcall(function()
                if pPlayer.GetScience then sciPerTurn = math.floor(pPlayer:GetScience() or 0) end
                if pPlayer.GetTotalJONSCulturePerTurn then culPerTurn = math.floor(pPlayer:GetTotalJONSCulturePerTurn() or 0) end
                if pPlayer.CalculateGoldRate then goldPerTurn = math.floor(pPlayer:CalculateGoldRate() or 0) end
            end)
            table.insert(data, '{"id": ' .. i .. ', "name": "' .. pName .. '", "civ": "' .. cName .. '", "dip": "' .. diplomacy .. '", "sci": ' .. sciPerTurn .. ', "cul": ' .. culPerTurn .. ', "gold": ' .. goldPerTurn)
            
            -- Cities
            table.insert(data, ', "cities": [')
            local firstCity = true
            for pCity in pPlayer:Cities() do
                if not firstCity then table.insert(data, ",") end
                firstCity = false
                local cId = pCity:GetID()
                local cityName = EscapeString(pCity:GetName())
                local x = pCity:GetX()
                local y = pCity:GetY()
                local pop = pCity:GetPopulation()
                local hp = pCity:GetDamage() 
                local maxHp = pCity:GetMaxHitPoints()
                
                local buildingName = "Nothing"
                local turnsLeft = 0
                local hammersPerTurn = 0
                local cSci = 0
                local cCul = 0
                pcall(function()
                    -- Directly check Unit, Building, and Project IDs (bypasses player visibility masking for AI cities)
                    local bID = pCity:GetProductionBuilding()
                    local uID = pCity:GetProductionUnit()
                    local prID = pCity:GetProductionProject()

                    if bID and bID > -1 and GameInfo.Buildings[bID] then
                        buildingName = Locale.ConvertTextKey(GameInfo.Buildings[bID].Description)
                    elseif uID and uID > -1 and GameInfo.Units[uID] then
                        buildingName = Locale.ConvertTextKey(GameInfo.Units[uID].Description)
                    elseif prID and prID > -1 and GameInfo.Projects[prID] then
                        buildingName = Locale.ConvertTextKey(GameInfo.Projects[prID].Description)
                    elseif pCity.GetProductionNameKey then
                        local key = pCity:GetProductionNameKey()
                        if key and key ~= "" and key ~= "TXT_KEY_PRODUCTION_NONE" then
                            buildingName = Locale.ConvertTextKey(key)
                        end
                    end

                    buildingName = EscapeString(buildingName)
                    if pCity.GetProductionTurnsLeft then turnsLeft = pCity:GetProductionTurnsLeft() or 0 end
                    if pCity.GetCurrentProductionDifferenceTimes100 then hammersPerTurn = math.floor((pCity:GetCurrentProductionDifferenceTimes100(false, false) or 0) / 100) end
                    if YieldTypes and YieldTypes.YIELD_SCIENCE and pCity.GetYieldRate then cSci = math.floor(pCity:GetYieldRate(YieldTypes.YIELD_SCIENCE) or 0) end
                    if pCity.GetJONSCulturePerTurn then cCul = math.floor(pCity:GetJONSCulturePerTurn() or 0) end
                end)
                table.insert(data, '{"id": ' .. cId .. ', "name": "' .. cityName .. '", "x": ' .. x .. ', "y": ' .. y .. ', "pop": ' .. pop .. ', "hp": ' .. (maxHp - hp) .. ', "maxhp": ' .. maxHp .. ', "build": "' .. buildingName .. '", "turns": ' .. turnsLeft .. ', "hammers": ' .. hammersPerTurn .. ', "sci": ' .. cSci .. ', "cul": ' .. cCul .. '}')
            end
            table.insert(data, ']')
            
            -- Units
            table.insert(data, ', "units": [')
            local firstUnit = true
            for pUnit in pPlayer:Units() do
                if not firstUnit then table.insert(data, ",") end
                firstUnit = false
                local uId = pUnit:GetID()
                local unitName = EscapeString(pUnit:GetName())
                local x = pUnit:GetX()
                local y = pUnit:GetY()
                local hp = pUnit:GetCurrHitPoints()
                local maxHp = pUnit:GetMaxHitPoints()
                local lvl = pUnit:GetLevel() or 1
                local xp = pUnit:GetExperience() or 0
                
                table.insert(data, '{"id": ' .. uId .. ', "name": "' .. unitName .. '", "x": ' .. x .. ', "y": ' .. y .. ', "hp": ' .. hp .. ', "max_hp": ' .. maxHp .. ', "lvl": ' .. lvl .. ', "xp": ' .. xp .. '}')
            end
            table.insert(data, ']}')
        end
    end
    
    local mapData = {}
    local mapWidth, mapHeight = Map.GetGridSize()
    for iPlot = 0, Map.GetNumPlots() - 1 do
        local pPlot = Map.GetPlotByIndex(iPlot)
        if pPlot then
            local pt = pPlot:GetPlotType()
            local f = pPlot:GetFeatureType()
            local r = pPlot:GetResourceType()
            local imp = pPlot:GetImprovementType()
            local o = pPlot:GetOwner()
            local rw = pPlot:IsWOfRiver() and 1 or 0
            local rnw = pPlot:IsNWOfRiver() and 1 or 0
            local rne = pPlot:IsNEOfRiver() and 1 or 0
            local h = (pt == PlotTypes.PLOT_HILLS) and 1 or 0
            local m = (pt == PlotTypes.PLOT_MOUNTAIN) and 1 or 0
            
            local tStr = string.format('{"x":%d,"y":%d,"t":%d', iPlot % mapWidth, math.floor(iPlot / mapWidth), pPlot:GetTerrainType())
            if f > -1 then tStr = tStr .. ',"f":' .. f end
            if r > -1 then tStr = tStr .. ',"r":' .. r end
            if imp > -1 then tStr = tStr .. ',"i":' .. imp end
            if o > -1 then tStr = tStr .. ',"o":' .. o end
            if rw == 1 then tStr = tStr .. ',"rw":1' end
            if rnw == 1 then tStr = tStr .. ',"rnw":1' end
            if rne == 1 then tStr = tStr .. ',"rne":1' end
            if h == 1 then tStr = tStr .. ',"h":1' end
            if m == 1 then tStr = tStr .. ',"m":1' end
            tStr = tStr .. '}'
            table.insert(mapData, tStr)
        end
    end
    
    local finalJson = '{' ..
        '"turn": ' .. turn .. ',' ..
        '"active_player": ' .. activePlayerID .. ',' ..
        '"resource_dict": {' .. table.concat(resDict, ",") .. '},' ..
        '"improvement_dict": {' .. table.concat(impDict, ",") .. '},' ..
        '"feature_dict": {' .. table.concat(featDict, ",") .. '},' ..
        '"players": [' .. table.concat(data, "") .. '],' ..
        '"map": [' .. table.concat(mapData, ",") .. ']' ..
    '}'
    
    print("CIV5_AI_BRIDGE_START")
    local chunkSize = 900
    for i = 1, #finalJson, chunkSize do
        print("CIV5_AI_BRIDGE_CHUNK:" .. string.sub(finalJson, i, i + chunkSize - 1))
    end
    print("CIV5_AI_BRIDGE_END")
    for i = 1, 20 do print("FLUSH_BUFFER") end
end

function ExportGameState()
    print("CIV5_AI_BRIDGE: Exporting state...")
    DumpGameState()
end

Events.ActivePlayerTurnStart.Add(ExportGameState)
Events.SequenceGameInitComplete.Add(ExportGameState)
Events.LoadScreenClose.Add(ExportGameState)

function RushWonders(playerID)
    local player = Players[playerID]
    if player and player:IsHuman() then
        for city in player:Cities() do
            local buildingID = city:GetProductionBuilding()
            if buildingID and buildingID ~= -1 then
                local buildingInfo = GameInfo.Buildings[buildingID]
                if buildingInfo then
                    local buildingClassInfo = GameInfo.BuildingClasses[buildingInfo.BuildingClass]
                    -- Check if it is a World Wonder or National Wonder
                    if buildingClassInfo and (buildingClassInfo.MaxGlobalInstances == 1 or buildingClassInfo.MaxPlayerInstances == 1) then
                        local needed = city:GetProductionNeeded()
                        local current = city:GetBuildingProduction(buildingID)
                        
                        -- If we haven't finished it yet, inject the remaining production
                        if current < needed then
                            city:ChangeProduction(needed - current)
                            local wonderName = Locale.ConvertTextKey(buildingInfo.Description)
                            print("CIV5_AI_BRIDGE: Rushed Wonder -> " .. wonderName)
                            Events.GameplayAlertMessage("GODMODE: Wonder Rushed -> " .. wonderName)
                        end
                    end
                end
            end
        end
    end
end
Events.ActivePlayerTurnStart.Add(RushWonders)



function OnUnitMoved(playerID, unitID, x, y)
    -- Don't trigger for invalid coordinates (e.g., unit dying/embarking into limbo)
    if x < 0 or y < 0 then return end
    
    local pPlayer = Players[playerID]
    if pPlayer then

        
        local pUnit = pPlayer:GetUnitByID(unitID)
        if pUnit then
            local unitName = EscapeString(pUnit:GetName())
            local hp = pUnit:GetCurrHitPoints()
            local str = 'CIV5_AI_BRIDGE_MINI:{"p":'..playerID..',"u":'..unitID..',"x":'..x..',"y":'..y..',"n":"'..unitName..'","hp":'..hp..'}'
            print(str)
            -- Flush buffer immediately for real-time responsiveness
            for i = 1, 5 do print("FLUSH_BUFFER") end
        end
    end
end

GameEvents.UnitSetXY.Add(OnUnitMoved)

-- Immediate export on load
pcall(function()
    if ContextPtr and ContextPtr:IsVisible() then
        ExportGameState()
    end
end)
