
stimulation_frequencies = {}
frequency_count = 0


processing_epoch_duration = nil
processing_epoch_interval = nil
processing_frequency_tolerance = nil
ssvep_duration = nil
ssvep_offset = nil

train_signal_csv = nil
train_stim_csv = nil
test_signal_csv = nil
test_stim_csv = nil
dsp_scale = nil


function initialize(box)

	dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")

	for value in box:get_setting(2):gmatch("%d+[.]?%d*") do
		table.insert(stimulation_frequencies, value)
		frequency_count = frequency_count + 1
	end

	processing_epoch_duration = box:get_setting(3)
	processing_epoch_interval = box:get_setting(4)
	processing_frequency_tolerance = box:get_setting(5)
	ssvep_duration = box:get_setting(6)
	ssvep_offset = box:get_setting(7)
	train_signal_csv = box:get_setting(8)
	train_stim_csv = box:get_setting(9)
	test_signal_csv = box:get_setting(10)
	test_stim_csv = box:get_setting(11)
	dsp_scale = box:get_setting(12)

end

function uninitialize(box)
end

function process(box)

	
	success = true 
	
	-- create configuration files for temporal filters

	scenario_path = box:get_config("${Player_ScenarioDirectory}")
		
	for i=1,frequency_count do
		cfg_file_name = scenario_path .. string.format("/configuration/temporal-filter-freq-%d.cfg", i)
		box:log("Info", "Writing file '" .. cfg_file_name .. "'")

		cfg_file = io.open(cfg_file_name, "w")
		if cfg_file == nil then
			box:log("Error", "Cannot write to [" .. cfg_file_name .. "]")
			box:log("Error", "Please copy the scenario folder to a directory with write access and use from there.")		
			return false
		end
		
		success = true
		success = success and cfg_file:write("<OpenViBE-SettingsOverride>\n")
		success = success and cfg_file:write("<SettingValue>Butterworth</SettingValue>\n")
		success = success and cfg_file:write("<SettingValue>Band pass</SettingValue>\n")
		success = success and cfg_file:write("<SettingValue>4</SettingValue>\n")
		success = success and cfg_file:write(string.format("<SettingValue>%g</SettingValue>\n", stimulation_frequencies[i] - processing_frequency_tolerance))
		success = success and cfg_file:write(string.format("<SettingValue>%g</SettingValue>\n", stimulation_frequencies[i] + processing_frequency_tolerance))
		success = success and cfg_file:write("<SettingValue>0.500000</SettingValue>\n")
		success = success and cfg_file:write("</OpenViBE-SettingsOverride>\n")
		
		cfg_file:close()
		
		if (success == false) then
			box:log("Error", box:get_config("Write error"))
			return false
		end
	
	end

    stim_based_epoching_cfg =  scenario_path .. string.format("/configuration/stimulation-based-epoching.cfg")
	box:log("Info", "Writing file '" .. stim_based_epoching_cfg .. "'")
	stim_based_epoching_cfg = io.open(stim_based_epoching_cfg, "w")
	if stim_based_epoching_cfg == nil then
		box:log("Error", "Cannot write to [" .. stim_based_epoching_cfg .. "]")
		box:log("Error", "Please copy the scenario folder to a directory with write access and use from there.")		
		return false
	end

	success = true
	success = success and stim_based_epoching_cfg:write("<OpenViBE-SettingsOverride>\n")
	success = success and stim_based_epoching_cfg:write(string.format("<SettingValue>%g</SettingValue>\n", ssvep_duration))
	success = success and stim_based_epoching_cfg:write(string.format("<SettingValue>%g</SettingValue>\n", ssvep_offset))
	success = success and stim_based_epoching_cfg:write("<SettingValue>OVTK_StimulationId_Target</SettingValue>\n")
	success = success and stim_based_epoching_cfg:write("</OpenViBE-SettingsOverride>\n")
	
	stim_based_epoching_cfg:close()
	
	if (success == false) then
		box:log("Error", box:get_config("Write error"))
		return false
	end

	-- Config for Files
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

	-- create configuration file for time based epoching
	cfg_file_name = scenario_path .. "/configuration/dsp_scale.cfg";
	
	box:log("Info", "Writing file '" .. cfg_file_name .. "'")

	cfg_file = io.open(cfg_file_name, "w")
	if cfg_file == nil then
		box:log("Error", "Cannot write to [" .. cfg_file_name .. "]")
		box:log("Error", "Please copy the scenario folder to a directory with write access and use from there.")
		return false
	end
		
	success = true
	success = success and cfg_file:write("<OpenViBE-SettingsOverride>\n")
	success = success and cfg_file:write(string.format("<SettingValue>%i*x</SettingValue>\n", dsp_scale))
	success = success and cfg_file:write("</OpenViBE-SettingsOverride>\n")
		
	cfg_file:close()

	if (success == false) then
		box:log("Error", box:get_config("Write error"))
		return false
	end

	
	-- notify the scenario that the configuration process is complete
	
	box:send_stimulation(1, OVTK_StimulationId_TrainCompleted, box:get_current_time() + 0.2, 0)

end
