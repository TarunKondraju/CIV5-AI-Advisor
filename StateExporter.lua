-- Civ 5 AI Bridge - State Exporter (Super Spy Mode)
-- Dumps extreme tactical game state to Lua.log every turn.

print("CIV5_AI_BRIDGE: Mod Loaded")

-- Set to false to stop the bridge from instantly completing your wonders every turn.
ENABLE_WONDER_RUSH = true

function EscapeString(str)
    if str == nil then return "" end
    str = string.gsub(str, '\\', '\\\\')
    str = string.gsub(str, '"', '\\"')
    str = string.gsub(str, '\n', '\\n')
    str = string.gsub(str, '\r', '\\r')
    return str
end

-- ===== Advisor block: everything needed for turn-by-turn guidance =====
local function J(s) return '"' .. EscapeString(tostring(s or "")) .. '"' end
local function T(key) if not key then return "" end return Locale.ConvertTextKey(key) end
local function N(v) v = tonumber(v) or 0; return tostring(math.floor(v)) end
local function Safe(fn, default)
    local ok, res = pcall(fn)
    if ok and res ~= nil then return res end
    return default
end
local function List(t) return "[" .. table.concat(t, ",") .. "]" end

-- Luxury + strategic resources a player has (available count includes imports)
function ResList(p)
    local t = {}
    for r in GameInfo.Resources() do
        local usage = Safe(function() return Game.GetResourceUsageType(r.ID) end, -1)
        if usage == ResourceUsageTypes.RESOURCEUSAGE_LUXURY or usage == ResourceUsageTypes.RESOURCEUSAGE_STRATEGIC then
            local avail = Safe(function() return p:GetNumResourceAvailable(r.ID, true) end, 0)
            local total = Safe(function() return p:GetNumResourceTotal(r.ID, false) end, 0)
            if (avail and avail ~= 0) or (total and total > 0) then
                table.insert(t, '{"n":' .. J(string.gsub(r.Type, "RESOURCE_", "")) ..
                    ',"lux":' .. tostring(usage == ResourceUsageTypes.RESOURCEUSAGE_LUXURY) ..
                    ',"avail":' .. N(avail) .. ',"own":' .. N(total) .. '}')
            end
        end
    end
    return List(t)
end

function BuildAdvisorJson(me)
    local pMe = Players[me]
    local teamMe = Teams[pMe:GetTeam()]
    local techs = teamMe:GetTeamTechs()
    local out = {}

    -- Economy / empire
    table.insert(out, '"era":' .. J(Safe(function() return T(GameInfo.Eras[pMe:GetCurrentEra()].Description) end, "")))
    table.insert(out, '"gold":' .. N(Safe(function() return pMe:GetGold() end, 0)))
    table.insert(out, '"gpt":' .. N(Safe(function() return pMe:CalculateGoldRate() end, 0)))
    table.insert(out, '"happiness":' .. N(Safe(function() return pMe:GetExcessHappiness() end, 0)))
    table.insert(out, '"golden_age_turns":' .. N(Safe(function() return pMe:GetGoldenAgeTurns() end, 0)))
    table.insert(out, '"golden_age_progress":' .. N(Safe(function() return pMe:GetGoldenAgeProgressMeter() end, 0)))
    table.insert(out, '"golden_age_needed":' .. N(Safe(function() return pMe:GetGoldenAgeProgressThreshold() end, 0)))
    table.insert(out, '"culture_stored":' .. N(Safe(function() return pMe:GetJONSCulture() end, 0)))
    table.insert(out, '"next_policy_cost":' .. N(Safe(function() return pMe:GetNextPolicyCost() end, 0)))
    table.insert(out, '"faith":' .. N(Safe(function() return pMe:GetFaith() end, 0)))
    table.insert(out, '"fpt":' .. N(Safe(function() return pMe:GetTotalFaithPerTurn() end, 0)))
    table.insert(out, '"has_pantheon":' .. tostring(Safe(function() return pMe:HasCreatedPantheon() end, false)))
    table.insert(out, '"religion":' .. J(Safe(function()
        local r = pMe:GetReligionCreatedByPlayer()
        if r and r > 0 then return T(GameInfo.Religions[r].Description) end
        return ""
    end, "")))
    table.insert(out, '"tourism":' .. N(Safe(function() return pMe:GetTourism() end, 0)))
    table.insert(out, '"trade_routes":' .. N(Safe(function() return pMe:GetNumInternationalTradeRoutesUsed() end, 0)) ..
        ',"trade_routes_max":' .. N(Safe(function() return pMe:GetNumInternationalTradeRoutesAvailable() end, 0)))
    table.insert(out, '"spies":' .. N(Safe(function() return #pMe:GetEspionageSpies() end, 0)))

    -- Research
    local cur = Safe(function() return pMe:GetCurrentResearch() end, -1)
    local curName, curTurns = "", 0
    if cur and cur > -1 then
        curName = T(GameInfo.Technologies[cur].Description)
        curTurns = Safe(function() return pMe:GetResearchTurnsLeft(cur, true) end, 0)
    end
    table.insert(out, '"research":' .. J(curName) .. ',"research_turns":' .. N(curTurns))
    local known, avail = {}, {}
    for t in GameInfo.Technologies() do
        if techs:HasTech(t.ID) then
            table.insert(known, J(T(t.Description)))
        elseif Safe(function() return pMe:CanResearch(t.ID) end, false) then
            table.insert(avail, '{"n":' .. J(T(t.Description)) .. ',"turns":' .. N(Safe(function() return pMe:GetResearchTurnsLeft(t.ID, true) end, 0)) .. '}')
        end
    end
    table.insert(out, '"techs_known":' .. List(known))
    table.insert(out, '"techs_available":' .. List(avail))

    -- Policies
    local branches, pols = {}, {}
    for b in GameInfo.PolicyBranchTypes() do
        if Safe(function() return pMe:IsPolicyBranchUnlocked(b.ID) end, false) then table.insert(branches, J(T(b.Description))) end
    end
    for p in GameInfo.Policies() do
        if Safe(function() return pMe:HasPolicy(p.ID) end, false) then table.insert(pols, J(T(p.Description))) end
    end
    table.insert(out, '"policy_branches":' .. List(branches))
    table.insert(out, '"policies":' .. List(pols))

    -- Projects (Apollo, spaceship parts, Manhattan...) for me
    local projs = {}
    for pr in GameInfo.Projects() do
        local c = Safe(function() return teamMe:GetProjectCount(pr.ID) end, 0)
        if c and c > 0 then table.insert(projs, '{"n":' .. J(T(pr.Description)) .. ',"count":' .. N(c) .. '}') end
    end
    table.insert(out, '"projects":' .. List(projs))

    -- Wonders I own
    local wonders = {}
    for pCity in pMe:Cities() do
        for b in GameInfo.Buildings() do
            local bc = GameInfo.BuildingClasses[b.BuildingClass]
            if bc and bc.MaxGlobalInstances == 1 and pCity:IsHasBuilding(b.ID) then
                table.insert(wonders, J(T(b.Description)))
            end
        end
    end
    table.insert(out, '"wonders":' .. List(wonders))

    -- Detailed cities
    local cities = {}
    for pCity in pMe:Cities() do
        local c = {}
        table.insert(c, '"name":' .. J(pCity:GetName()))
        table.insert(c, '"x":' .. pCity:GetX() .. ',"y":' .. pCity:GetY() .. ',"pop":' .. pCity:GetPopulation())
        table.insert(c, '"capital":' .. tostring(pCity:IsCapital()))
        table.insert(c, '"puppet":' .. tostring(Safe(function() return pCity:IsPuppet() end, false)))
        table.insert(c, '"resistance":' .. N(Safe(function() return pCity:GetResistanceTurns() end, 0)))
        table.insert(c, '"hp":' .. N(pCity:GetMaxHitPoints() - pCity:GetDamage()) .. ',"maxhp":' .. N(pCity:GetMaxHitPoints()))
        table.insert(c, '"strength":' .. N(Safe(function() return pCity:GetStrengthValue() / 100 end, 0)))
        if YieldTypes then
            table.insert(c, '"food":' .. N(Safe(function() return pCity:FoodDifference() end, 0)))
            table.insert(c, '"growth_turns":' .. N(Safe(function() return pCity:GetFoodTurnsLeft() end, 0)))
            table.insert(c, '"prod":' .. N(Safe(function() return pCity:GetCurrentProductionDifferenceTimes100(false, false) / 100 end, 0)))
            table.insert(c, '"gold":' .. N(Safe(function() return pCity:GetYieldRate(YieldTypes.YIELD_GOLD) end, 0)))
            table.insert(c, '"sci":' .. N(Safe(function() return pCity:GetYieldRate(YieldTypes.YIELD_SCIENCE) end, 0)))
            table.insert(c, '"cul":' .. N(Safe(function() return pCity:GetJONSCulturePerTurn() end, 0)))
            table.insert(c, '"faith":' .. N(Safe(function() return pCity:GetFaithPerTurn() end, 0)))
        end
        table.insert(c, '"build":' .. J(Safe(function()
            local k = pCity:GetProductionNameKey()
            if k and k ~= "" then return T(k) end
            return "Nothing"
        end, "Nothing")) .. ',"build_turns":' .. N(Safe(function() return pCity:GetProductionTurnsLeft() end, 0)))
        local has, canB, canU, canP = {}, {}, {}, {}
        for b in GameInfo.Buildings() do
            if pCity:IsHasBuilding(b.ID) then
                table.insert(has, J(T(b.Description)))
            elseif Safe(function() return pCity:CanConstruct(b.ID) end, false) then
                table.insert(canB, '{"n":' .. J(T(b.Description)) .. ',"turns":' .. N(Safe(function() return pCity:GetBuildingProductionTurnsLeft(b.ID, 0) end, 0)) .. ',"buy":' .. N(Safe(function() return pCity:GetBuildingPurchaseCost(b.ID) end, 0)) .. '}')
            end
        end
        for u in GameInfo.Units() do
            if Safe(function() return pCity:CanTrain(u.ID) end, false) then
                table.insert(canU, J(T(u.Description)))
            end
        end
        for pr in GameInfo.Projects() do
            if Safe(function() return pCity:CanCreate(pr.ID) end, false) then
                table.insert(canP, J(T(pr.Description)))
            end
        end
        table.insert(c, '"buildings":' .. List(has))
        table.insert(c, '"can_build":' .. List(canB))
        table.insert(c, '"can_train":' .. List(canU))
        table.insert(c, '"can_project":' .. List(canP))
        table.insert(c, '"specialists":' .. N(Safe(function() return pCity:GetSpecialistCount(0) + pCity:GetSpecialistCount(1) + pCity:GetSpecialistCount(2) + pCity:GetSpecialistCount(3) + pCity:GetSpecialistCount(4) + pCity:GetSpecialistCount(5) end, 0)))
        -- v1.2: citizen management data
        table.insert(c, '"focus":' .. N(Safe(function() return pCity:GetFocusType() end, -1)))
        table.insert(c, '"connected":' .. tostring(Safe(function() return pCity:IsCapital() or pMe:IsCapitalConnectedToCity(pCity) end, false)))
        table.insert(c, '"great_work_slots":' .. N(Safe(function()
            local n = 0
            for b in GameInfo.Buildings() do
                if (b.GreatWorkCount or 0) > 0 and pCity:IsHasBuilding(b.ID) then n = n + b.GreatWorkCount end
            end
            return n
        end, 0)) .. ',"great_works":' .. N(Safe(function() return pCity:GetNumGreatWorks() end, 0)))
        table.insert(c, '"unemployed":' .. N(Safe(function() return pCity:GetSpecialistCount(GameInfo.Specialists.SPECIALIST_CITIZEN.ID) end, 0)))
        table.insert(c, '"religion":' .. J(Safe(function()
            local r = pCity:GetReligiousMajority()
            if r and r >= 0 then return T(GameInfo.Religions[r].Description) end
            return ""
        end, "")))
        local spec = {}
        for s in GameInfo.Specialists() do
            if s.Type ~= "SPECIALIST_CITIZEN" then
                local slots = 0
                for b in GameInfo.Buildings() do
                    if b.SpecialistType == s.Type and (b.SpecialistCount or 0) > 0 and pCity:IsHasBuilding(b.ID) then
                        slots = slots + b.SpecialistCount
                    end
                end
                local cnt = Safe(function() return pCity:GetSpecialistCount(s.ID) end, 0)
                local gpp = Safe(function() return pCity:GetSpecialistGreatPersonProgress(s.ID) end, 0)
                if slots > 0 or cnt > 0 or gpp > 0 then
                    table.insert(spec, '{"n":' .. J(T(s.Description)) .. ',"count":' .. N(cnt) .. ',"slots":' .. N(slots) .. ',"gpp":' .. N(gpp) .. '}')
                end
            end
        end
        table.insert(c, '"specialist_slots":' .. List(spec))
        local tiles = {}
        Safe(function()
            local yF, yP, yG, yS = YieldTypes.YIELD_FOOD, YieldTypes.YIELD_PRODUCTION, YieldTypes.YIELD_GOLD, YieldTypes.YIELD_SCIENCE
            local yC, yFa = YieldTypes.YIELD_CULTURE, YieldTypes.YIELD_FAITH
            for i = 0, pCity:GetNumCityPlots() - 1 do
                local plot = pCity:GetCityIndexPlot(i)
                if plot and plot:GetOwner() == me and not (plot:GetX() == pCity:GetX() and plot:GetY() == pCity:GetY()) then
                    local wc = plot:GetWorkingCity()
                    if wc == nil or wc:GetID() == pCity:GetID() then
                        local function Y(t) if t == nil then return 0 end return plot:CalculateYield(t, true) or 0 end
                        table.insert(tiles, '[' .. plot:GetX() .. ',' .. plot:GetY() .. ',' .. N(Y(yF)) .. ',' .. N(Y(yP)) .. ',' .. N(Y(yG)) .. ',' ..
                            N(Y(yS)) .. ',' .. N(Y(yC)) .. ',' .. N(Y(yFa)) .. ',' .. (pCity:IsWorkingPlot(plot) and 1 or 0) .. ',' ..
                            plot:GetResourceType() .. ',' .. plot:GetImprovementType() .. ',' .. (plot:IsImprovementPillaged() and 1 or 0) .. ']')
                    end
                end
            end
            return true
        end, false)
        table.insert(c, '"tiles":' .. List(tiles))
        table.insert(cities, '{' .. table.concat(c, ",") .. '}')
    end
    table.insert(out, '"cities":' .. List(cities))

    -- Rivals: diplomacy + victory progress
    local rivals, cs = {}, {}
    for i = 0, GameDefines.MAX_CIV_PLAYERS - 1 do
        local p = Players[i]
        if i ~= me and p and p:IsAlive() and not p:IsBarbarian() then
            local team = Teams[p:GetTeam()]
            local met = Safe(function() return teamMe:IsHasMet(p:GetTeam()) end, false)
            local war = Safe(function() return teamMe:IsAtWar(p:GetTeam()) end, false)
            if p:IsMinorCiv() then
                local ally = Safe(function() return p:GetAlly() end, -1)
                local quests = {}
                Safe(function()
                    for k, v in pairs(MinorCivQuestTypes) do
                        if type(v) == "number" and v >= 0 and p:IsMinorCivActiveQuestForPlayer(me, v) then
                            table.insert(quests, J(string.gsub(k, "MINOR_CIV_QUEST_", "")))
                        end
                    end
                    return true
                end, false)
                local cap = Safe(function() return p:GetCapitalCity() end, nil)
                table.insert(cs, '{"name":' .. J(p:GetName()) .. ',"met":' .. tostring(met) .. ',"war":' .. tostring(war) ..
                    ',"influence":' .. N(Safe(function() return p:GetMinorCivFriendshipWithMajor(me) end, 0)) ..
                    ',"ally":' .. J(Safe(function() if ally and ally > -1 then return Players[ally]:GetName() end return "" end, "")) ..
                    ',"ally_influence":' .. N(Safe(function() if ally and ally > -1 and ally ~= me then return p:GetMinorCivFriendshipWithMajor(ally) end return 0 end, 0)) ..
                    ',"type":' .. J(Safe(function() return T(GameInfo.MinorCivTraits[p:GetMinorCivTrait()].Description) end, "")) ..
                    ',"personality":' .. N(Safe(function() return p:GetPersonality() end, -1)) ..
                    ',"x":' .. N(cap and cap:GetX() or -1) .. ',"y":' .. N(cap and cap:GetY() or -1) ..
                    ',"protected_by_me":' .. tostring(Safe(function() return pMe:IsProtectingMinor(i) end, false)) ..
                    ',"can_bully_gold":' .. tostring(Safe(function() return p:CanMajorBullyGold(me) end, false)) ..
                    ',"bully_gold":' .. N(Safe(function() return p:GetMinorCivBullyGoldAmount(me) end, 0)) ..
                    ',"quests":' .. List(quests) .. '}')
            else
                local nTech = Safe(function() return team:GetTeamTechs():GetNumTechsKnown() end, 0)
                local parts = {}
                for pr in GameInfo.Projects() do
                    local c = Safe(function() return team:GetProjectCount(pr.ID) end, 0)
                    if c and c > 0 then table.insert(parts, J(T(pr.Description) .. " x" .. c)) end
                end
                local nInfluenced = 0
                for j = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
                    if j ~= i and Players[j] and Players[j]:IsAlive() then
                        local lvl = Safe(function() return p:GetInfluenceLevel(j) end, 0)
                        if lvl and lvl >= 4 then nInfluenced = nInfluenced + 1 end
                    end
                end
                table.insert(rivals, '{"name":' .. J(p:GetName()) .. ',"civ":' .. J(p:GetCivilizationShortDescription()) ..
                    ',"met":' .. tostring(met) .. ',"war":' .. tostring(war) ..
                    ',"dof":' .. tostring(Safe(function() return pMe:IsDoF(i) end, false)) ..
                    ',"denounced_by_me":' .. tostring(Safe(function() return pMe:IsDenouncedPlayer(i) end, false)) ..
                    ',"denounced_me":' .. tostring(Safe(function() return p:IsDenouncedPlayer(me) end, false)) ..
                    ',"score":' .. N(Safe(function() return p:GetScore() end, 0)) ..
                    ',"techs":' .. N(nTech) ..
                    ',"era":' .. J(Safe(function() return T(GameInfo.Eras[p:GetCurrentEra()].Description) end, "")) ..
                    ',"tourism":' .. N(Safe(function() return p:GetTourism() end, 0)) ..
                    ',"influential_over":' .. N(nInfluenced) ..
                    ',"my_influence_on_them":' .. N(Safe(function() return pMe:GetInfluenceLevel(i) end, 0)) ..
                    ',"their_influence_on_me":' .. N(Safe(function() return p:GetInfluenceLevel(me) end, 0)) ..
                    ',"holds_own_capital":' .. tostring(Safe(function() local c = p:GetCapitalCity(); return c ~= nil and c:IsOriginalCapital() and c:GetOriginalOwner() == i end, false)) ..
                    ',"projects":' .. List(parts) ..
                    ',"military":' .. N(Safe(function() return p:GetMilitaryMight() end, 0)) ..
                    ',"treasury":' .. N(Safe(function() return p:GetGold() end, 0)) ..
                    ',"gpt":' .. N(Safe(function() return p:CalculateGoldRate() end, 0)) ..
                    ',"happiness":' .. N(Safe(function() return p:GetExcessHappiness() end, 0)) ..
                    ',"open_borders_with_me":' .. tostring(Safe(function() return team:IsAllowsOpenBordersToTeam(pMe:GetTeam()) end, false)) ..
                    ',"religion":' .. J(Safe(function() local r = p:GetReligionCreatedByPlayer(); if r and r > 0 then return T(GameInfo.Religions[r].Description) end return "" end, "")) ..
                    ',"ideology":' .. J(Safe(function()
                        for b in GameInfo.PolicyBranchTypes() do
                            if b.PurchaseByLevel and p:IsPolicyBranchUnlocked(b.ID) then return T(b.Description) end
                        end
                        return ""
                    end, "")) ..
                    ',"resources":' .. ResList(p) .. '}')
            end
        end
    end
    table.insert(out, '"my_resources":' .. ResList(pMe))
    table.insert(out, '"my_ideology":' .. J(Safe(function()
        for b in GameInfo.PolicyBranchTypes() do
            if b.PurchaseByLevel and pMe:IsPolicyBranchUnlocked(b.ID) then return T(b.Description) end
        end
        return ""
    end, "")))
    -- Religion / pantheon options
    table.insert(out, '"pantheons_available":' .. List(Safe(function()
        local t = {}
        if pMe:HasCreatedPantheon() then return t end
        for _, id in ipairs(Game.GetAvailablePantheonBeliefs()) do
            local b = GameInfo.Beliefs[id]
            table.insert(t, '{"n":' .. J(T(b.ShortDescription)) .. ',"d":' .. J(T(b.Description)) .. '}')
        end
        return t
    end, {})))
    table.insert(out, '"faith_for_pantheon":' .. N(Safe(function() return Game.GetMinimumFaithNextPantheon() end, 0)))
    table.insert(out, '"faith_for_prophet":' .. N(Safe(function() return pMe:GetMinimumFaithNextGreatProphet() end, 0)))
    table.insert(out, '"religions_left":' .. N(Safe(function() return Game.GetNumReligionsStillToFound() end, 0)))
    table.insert(out, '"happiness_total":' .. N(Safe(function() return pMe:GetHappiness() end, 0)) ..
        ',"unhappiness_total":' .. N(Safe(function() return pMe:GetUnhappiness() end, 0)))
    -- Wars between AIs (an AI busy elsewhere is less likely to attack you)
    local wars = {}
    for i = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
        for j = i + 1, GameDefines.MAX_MAJOR_CIVS - 1 do
            local a, b = Players[i], Players[j]
            if i ~= me and j ~= me and a and b and a:IsAlive() and b:IsAlive() and not a:IsMinorCiv() and not b:IsMinorCiv()
                and Safe(function() return Teams[a:GetTeam()]:IsAtWar(b:GetTeam()) end, false) then
                table.insert(wars, J(a:GetCivilizationShortDescription() .. " vs " .. b:GetCivilizationShortDescription()))
            end
        end
    end
    table.insert(out, '"ai_wars":' .. List(wars))
    -- Trade routes in use
    table.insert(out, '"my_trade_routes":' .. List(Safe(function()
        local t = {}
        for _, r in ipairs(pMe:GetTradeRoutes()) do
            table.insert(t, '{"from":' .. J(r.FromCityName) .. ',"to":' .. J(r.ToCityName) .. ',"to_civ":' .. J(r.ToCivilizationShortDescription or "") ..
                ',"domain":' .. N(r.Domain) .. ',"turns_left":' .. N(r.TurnsLeft) ..
                ',"from_gold":' .. N((r.FromGPT or 0) / 100) .. ',"from_sci":' .. N((r.FromScience or 0) / 100) ..
                ',"to_food":' .. N((r.ToFood or 0) / 100) .. ',"to_prod":' .. N((r.ToProduction or 0) / 100) .. '}')
        end
        return t
    end, {})))
    -- World Congress
    table.insert(out, '"congress":' .. Safe(function()
        if not Game.GetNumActiveLeagues or Game.GetNumActiveLeagues() == 0 then return '{"active":false}' end
        local league = Game.GetActiveLeague()
        return '{"active":true,"my_votes":' .. N(league:CalculateStartingVotesForMember(me)) ..
            ',"turns_until_session":' .. N(league:GetTurnsUntilSession()) ..
            ',"host":' .. J(Safe(function() return Players[league:GetHostMember()]:GetCivilizationShortDescription() end, "")) .. '}'
    end, '{"active":false}'))
    -- What is waiting for a decision this turn
    local todo = {}
    if Safe(function() return pMe:GetCurrentResearch() == -1 end, false) then table.insert(todo, J("Choose research")) end
    if Safe(function() return pMe:GetJONSCulture() >= pMe:GetNextPolicyCost() end, false) then table.insert(todo, J("Adopt a social policy")) end
    if Safe(function() return not pMe:HasCreatedPantheon() and pMe:GetFaith() >= Game.GetMinimumFaithNextPantheon() end, false) then table.insert(todo, J("Found a pantheon")) end
    if Safe(function() return pMe:GetNumFreeTechs() > 0 end, false) then table.insert(todo, J("Pick a free tech")) end
    if Safe(function() return pMe.GetNumFreePolicies ~= nil and pMe:GetNumFreePolicies() > 0 end, false) then table.insert(todo, J("Pick a free policy")) end
    for pCity in pMe:Cities() do
        if Safe(function() return pCity:GetProductionNameKey() == nil or pCity:GetProductionNameKey() == "" end, false) then
            table.insert(todo, J("Set production in " .. pCity:GetName()))
        end
    end
    table.insert(out, '"todo":' .. List(todo))
    table.insert(out, '"my_techs":' .. N(Safe(function() return techs:GetNumTechsKnown() end, 0)))
    table.insert(out, '"my_military":' .. N(Safe(function() return pMe:GetMilitaryMight() end, 0)))
    table.insert(out, '"rivals":' .. List(rivals))
    table.insert(out, '"city_states":' .. List(cs))
    table.insert(out, '"game_speed":' .. J(Safe(function() return T(GameInfo.GameSpeeds[PreGame.GetGameSpeed()].Description) end, "")))
    table.insert(out, '"difficulty":' .. J(Safe(function() return T(GameInfo.HandicapInfos[pMe:GetHandicapType()].Description) end, "")))

    return '{' .. table.concat(out, ",") .. '}'
end

function AdvisorJsonSafe(me)
    local ok, res = pcall(BuildAdvisorJson, me)
    if ok then return res end
    print("CIV5_AI_BRIDGE: advisor block failed: " .. tostring(res))
    return '{"error":' .. J(res) .. '}'
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
                
                -- v1.2: unit type, strength, domain (+ details for my own units)
                local ui = GameInfo.Units[pUnit:GetUnitType()]
                local extra = ', "type": "' .. (ui and ui.Type or "") .. '", "str": ' .. ((ui and ui.Combat) or 0) ..
                    ', "rstr": ' .. ((ui and ui.RangedCombat) or 0) .. ', "dom": "' .. ((ui and ui.Domain) or "") .. '"' ..
                    ', "civilian": ' .. tostring(((ui and ui.Combat) or 0) == 0 and ((ui and ui.RangedCombat) or 0) == 0) ..
                    ', "embarked": ' .. tostring(Safe(function() return pUnit:IsEmbarked() end, false))
                if i == activePlayerID then
                    local upType = Safe(function() return pUnit:GetUpgradeUnitType() end, -1)
                    local build = Safe(function()
                        local b = pUnit:GetBuildType()
                        if b and b > -1 then return GameInfo.Builds[b].Type end
                        return ""
                    end, "")
                    extra = extra .. ', "moves": ' .. N(Safe(function() return pUnit:MovesLeft() / GameDefines.MOVE_DENOMINATOR end, 0)) ..
                        ', "max_moves": ' .. N(Safe(function() return pUnit:MaxMoves() / GameDefines.MOVE_DENOMINATOR end, 0)) ..
                        ', "fortified": ' .. tostring(Safe(function() return pUnit:GetFortifyTurns() > 0 end, false)) ..
                        ', "automated": ' .. tostring(Safe(function() return pUnit:IsAutomated() end, false)) ..
                        ', "can_promote": ' .. tostring(Safe(function() return pUnit:IsPromotionReady() end, false)) ..
                        ', "can_upgrade": ' .. tostring(Safe(function() return pUnit:CanUpgradeRightNow(false) end, false)) ..
                        ', "upgrade_to": "' .. Safe(function() if upType and upType > -1 then return GameInfo.Units[upType].Type end return "" end, "") .. '"' ..
                        ', "upgrade_cost": ' .. N(Safe(function() if upType and upType > -1 then return pUnit:UpgradePrice(upType) end return 0 end, 0)) ..
                        ', "build": "' .. build .. '"'
                end
                table.insert(data, '{"id": ' .. uId .. ', "name": "' .. unitName .. '", "x": ' .. x .. ', "y": ' .. y .. ', "hp": ' .. hp .. ', "max_hp": ' .. maxHp .. ', "lvl": ' .. lvl .. ', "xp": ' .. xp .. extra .. '}')
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
            -- v1.2: fog of war (from the active player's view), roads, pillage, lakes
            local activeTeam = Players[activePlayerID]:GetTeam()
            if not pPlot:IsRevealed(activeTeam, false) then tStr = tStr .. ',"fog":1'
            elseif pPlot:IsVisible(activeTeam, false) then tStr = tStr .. ',"vis":1' end
            local rt = pPlot:GetRouteType()
            if rt and rt > -1 then tStr = tStr .. ',"rt":' .. rt end
            if pPlot:IsImprovementPillaged() then tStr = tStr .. ',"pil":1' end
            if pPlot:IsLake() then tStr = tStr .. ',"lake":1' end
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
        '"advisor": ' .. AdvisorJsonSafe(activePlayerID) .. ',' ..
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
    if not ENABLE_WONDER_RUSH then return end
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
