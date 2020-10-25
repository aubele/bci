
stimulation_frequencies = {}
frequency_count = 0


processing_epoch_duration = nil
processing_epoch_interval = nil

train_signal_csv = nil
train_stim_csv = nil
test_signal_csv = nil
test_stim_csv = nil


function initialize(box)

	dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")

	processing_epoch_duration = box:get_setting(2)
	processing_epoch_interval = box:get_setting(3)

	train_signal_csv = box:get_setting(4)
	train_stim_csv = box:get_setting(5)
	test_signal_csv = box:get_setting(6)
	test_stim_csv = box:get_setting(7)

end

function uninitialize(box)
end

function process(box)

	
	success = true 
	
	-- create configuration files for temporal filters

	scenario_path = box:get_config("${Player_ScenarioDirectory}")

    

	
	-- Train Signal

	cfg_file_name = scenario_path .. "/configuration/train_signal_csv.cfg";
	
	box:log("Info", "Writing file '" .. cfg_file_name .. "'")

	cfg_file = io.open(cfg_file_name, "w")
	if cfg_file == nil then
		box:log("Error", "Cannot write to [" .. cfg_file_name .. "]")
		box:log("Error", "Please copy the scenario folder to a directory with write access and use from there.")
		return false
	end
		
	success = true
	success = success and cfg_file:write("<OpenViBE-SettingsOverride>\n")
	success = success and cfg_file:write(string.format("<SettingValue>%s</SettingValue>\n", train_signal_csv))
	success = success and cfg_file:write(string.format("<SettingValue>;</SettingValue>\n"))
	success = success and cfg_file:write(string.format("<SettingValue>true</SettingValue>\n"))
	success = success and cfg_file:write(string.format("<SettingValue>32</SettingValue>\n"))
	success = success and cfg_file:write("</OpenViBE-SettingsOverride>\n")
		
	cfg_file:close()

	if (success == false) then
		box:log("Error", box:get_config("Write error"))
		return false
	end

	-- Train Stim

	cfg_file_name = scenario_path .. "/configuration/train_stim_csv.cfg";
	
	box:log("Info", "Writing file '" .. cfg_file_name .. "'")

	cfg_file = io.open(cfg_file_name, "w")
	if cfg_file == nil then
		box:log("Error", "Cannot write to [" .. cfg_file_name .. "]")
		box:log("Error", "Please copy the scenario folder to a directory with write access and use from there.")
		return false
	end
		
	success = true
	success = success and cfg_file:write("<OpenViBE-SettingsOverride>\n")
	success = success and cfg_file:write(string.format("<SettingValue>%s</SettingValue>\n", train_stim_csv))
	success = success and cfg_file:write(string.format("<SettingValue>;</SettingValue>\n"))
	success = success and cfg_file:write(string.format("<SettingValue>true</SettingValue>\n"))
	success = success and cfg_file:write(string.format("<SettingValue>0</SettingValue>\n"))
	success = success and cfg_file:write("</OpenViBE-SettingsOverride>\n")
		
	cfg_file:close()

	if (success == false) then
		box:log("Error", box:get_config("Write error"))
		return false
	end

	-- Test Signal

	cfg_file_name = scenario_path .. "/configuration/test_signal_csv.cfg";
	
	box:log("Info", "Writing file '" .. cfg_file_name .. "'")

	cfg_file = io.open(cfg_file_name, "w")
	if cfg_file == nil then
		box:log("Error", "Cannot write to [" .. cfg_file_name .. "]")
		box:log("Error", "Please copy the scenario folder to a directory with write access and use from there.")
		return false
	end
		
	success = true
	success = success and cfg_file:write("<OpenViBE-SettingsOverride>\n")
	success = success and cfg_file:write(string.format("<SettingValue>%s</SettingValue>\n", test_signal_csv))
	success = success and cfg_file:write(string.format("<SettingValue>;</SettingValue>\n"))
	success = success and cfg_file:write(string.format("<SettingValue>true</SettingValue>\n"))
	success = success and cfg_file:write(string.format("<SettingValue>32</SettingValue>\n"))
	success = success and cfg_file:write("</OpenViBE-SettingsOverride>\n")
		
	cfg_file:close()

	if (success == false) then
		box:log("Error", box:get_config("Write error"))
		return false
	end

	-- Test Stim

	cfg_file_name = scenario_path .. "/configuration/test_stim_csv.cfg";
	
	box:log("Info", "Writing file '" .. cfg_file_name .. "'")

	cfg_file = io.open(cfg_file_name, "w")
	if cfg_file == nil then
		box:log("Error", "Cannot write to [" .. cfg_file_name .. "]")
		box:log("Error", "Please copy the scenario folder to a directory with write access and use from there.")
		return false
	end
		
	success = true
	success = success and cfg_file:write("<OpenViBE-SettingsOverride>\n")
	success = success and cfg_file:write(string.format("<SettingValue>%s</SettingValue>\n", test_stim_csv))
	success = success and cfg_file:write(string.format("<SettingValue>;</SettingValue>\n"))
	success = success and cfg_file:write(string.format("<SettingValue>true</SettingValue>\n"))
	success = success and cfg_file:write(string.format("<SettingValue>0</SettingValue>\n"))
	success = success and cfg_file:write("</OpenViBE-SettingsOverride>\n")
		
	cfg_file:close()

	if (success == false) then
		box:log("Error", box:get_config("Write error"))
		return false
	end


	-- create configuration file for time based epoching
	cfg_file_name = scenario_path .. "/configuration/time-based-epoching.cfg";
	
	box:log("Info", "Writing file '" .. cfg_file_name .. "'")

	cfg_file = io.open(cfg_file_name, "w")
	if cfg_file == nil then
		box:log("Error", "Cannot write to [" .. cfg_file_name .. "]")
		box:log("Error", "Please copy the scenario folder to a directory with write access and use from there.")
		return false
	end
		
	success = true
	success = success and cfg_file:write("<OpenViBE-SettingsOverride>\n")
	success = success and cfg_file:write(string.format("<SettingValue>%g</SettingValue>\n", processing_epoch_duration))
	success = success and cfg_file:write(string.format("<SettingValue>%g</SettingValue>\n", processing_epoch_interval))
	success = success and cfg_file:write("</OpenViBE-SettingsOverride>\n")
		
	cfg_file:close()

	if (success == false) then
		box:log("Error", box:get_config("Write error"))
		return false
	end
	
	-- notify the scenario that the configuration process is complete
	
	box:send_stimulation(1, OVTK_StimulationId_TrainCompleted, box:get_current_time() + 0.2, 0)

end
