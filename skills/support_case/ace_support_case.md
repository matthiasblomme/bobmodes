# ibm case support skill

## Main goal

- identify the topic that is wrong
- help the user gather information to make the creation and handling of an ibm support case as easy as possible

## some key points you need to know

- ACE version
- node name
- integration server name, if the error is limited to one or more integration servers
- short description of the issue the user sees
- timing the issue occured (in order to be able to extract from the event viewer, or check the logs for relevant entries)
- any related actions that have been taken?
- do you have access to the runtime
	- yes: you need to ask MQSI_BASE_FILEPATH in order to have access to the tools
	- no: you only need to supply the commands for the user to runtime
- error description or abend file

## what you need to do

- supply/request system info `mqsiservice -v`
- supply the necesseray and addditional logs
	- https://www.ibm.com/docs/en/app-connect/13.0.x?topic=software-troubleshooting-support
	- export event viewer (only a window of 30 min before earliest occurrence to 30 min after latest occurrence, not the full views)
	- console logs or stdout/stderr (node + per-IS logs under <NODE_WORK_DIR>\components\<NODE>\log\ and \servers\<IS>\; ask for the work-data root, don't assume %ProgramData%\IBM\MQSI)
	- ace data collector for node and IS (should the issue be about a specific IS) https://www.ibm.com/support/pages/node/886323
	- user and service trace output, should that be relevant 
		https://www.ibm.com/docs/en/app-connect/13.0.x?topic=support-using-trace
		https://www.ibm.com/docs/en/app-connect/13.0.x?topic=trace-user 
		https://www.ibm.com/docs/en/app-connect/13.0.x?topic=trace-service
	- all this info is supplied in your references directory
- project interchange with relevant applications and libraries
- possible node backup, only after user agrees and if it could be of addedd value
- any specific setup, such as shared-classes
- abend files

You can create most of these exports yourself. If you know where the ace runtime is and what node or standalone servers or containers are being used, you can run these commands and provide output bundles in an aptly named folder.

## additional actions before finishing this skill

analyze the documents under references/documentation and provide a summary of what you found. Write that summery for reference by you for future runs. The documentation is only here to initialy create the skill and can be deleted and updated on the fly and does not belong in the skill.

## Building this skill

Check the documentation and build an internal descission tree of actions you and/or the user needs to take to provide sufficient documentation to present to IBM in a support case for ACE

Check the provided info and supply any insights or solutions you might think off as well.

Create the skill by taking into account everything else that you need to know

