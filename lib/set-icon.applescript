use framework "Foundation"
use framework "AppKit"
use scripting additions

on run argv
	set iconFile to item 1 of argv
	set targetFile to item 2 of argv
	set img to current application's NSImage's alloc()'s initWithContentsOfFile:iconFile
	if img is missing value then error "cannot read icon: " & iconFile
	set ok to current application's NSWorkspace's sharedWorkspace()'s setIcon:img forFile:targetFile options:0
	if ok is false then error "cannot set icon on: " & targetFile
	return "ok"
end run
