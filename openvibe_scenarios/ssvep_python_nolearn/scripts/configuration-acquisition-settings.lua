
stimulation_frequencies = {}
frequency_count = 0

target_light_color = {}
target_dark_color = {}
training_target_size = {}
training_targets_positions = {}


function initialize(box)

	dofile(box:get_config("${Path_Data}") .. "/plugins/stimulation/lua-stimulator-stim-codes.lua")

	for value in box:get_setting(2):gmatch("%d+") do
		table.insert(target_light_color, value)
	end

	for value in box:get_setting(3):gmatch("%d+") do
		table.insert(target_dark_color, value)
	end

	for value in box:get_setting(4):gmatch("%d+[.]?%d*") do
		table.insert(stimulation_frequencies, value)
		frequency_count = frequency_count + 1
	end

end

function uninitialize(box)
end

function process(box)

	while box:keep_processing() and box:get_stimulation_count(1) == 0 do
		box:sleep()
	end

	box:log("Info", box:get_config("Writing additional configuration to '${CustomConfigurationPrefix${OperatingSystem}}-ssvep-demo${CustomConfigurationSuffix${OperatingSystem}}'"))

	cfg_file = assert(io.open(box:get_config("${CustomConfigurationPrefix${OperatingSystem}}-ssvep-demo${CustomConfigurationSuffix${OperatingSystem}}"), "a"))

	success = true 
	success = success and cfg_file:write("SSVEP_TargetLightColourRed = ", target_light_color[1] / 100, "\n")
	success = success and cfg_file:write("SSVEP_TargetLightColourGreen = ", target_light_color[2] / 100, "\n")
	success = success and cfg_file:write("SSVEP_TargetLightColourBlue = ", target_light_color[3] / 100, "\n")
	success = success and cfg_file:write("SSVEP_TargetDarkColourRed = ", target_dark_color[1] / 100, "\n")
	success = success and cfg_file:write("SSVEP_TargetDarkColourGreen = ", target_dark_color[2] / 100, "\n")
	success = success and cfg_file:write("SSVEP_TargetDarkColourBlue = ", target_dark_color[3] / 100, "\n")

	for i=1,frequency_count do
		success = success and cfg_file:write("SSVEP_Frequency_", i, " = ", string.format("%g", stimulation_frequencies[i]), "\n")
	end
	
	cfg_file:close()

	if (success == false) then
		box:log("Error", box:get_config("Write error"))
		return false
	end

	if (success == false) then
		box:log("Error", box:get_config("Write error"))
		return false
	end
	
	-- notify the scenario that the configuration process is complete
	
	box:send_stimulation(1, OVTK_StimulationId_TrainCompleted, box:get_current_time() + 0.2, 0)

end
