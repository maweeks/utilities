.PHONY: help listAllExistingRules listExistingRules addRuleToSecurityGroup deleteExistingRules showIp updateAwsIp

include variables.mk

help:                       ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

listAllExistingRules:       ## Get all the existing ingress rules
	@aws ec2 describe-security-groups --region ${REGION} --group-ids ${SECURITY_GROUP_ID} | jq -c '.SecurityGroups[0].IpPermissions[] | ({ FromPort: .FromPort, ToPort: .ToPort, IpProtocol: .IpProtocol } + ( .IpRanges[] | { CidrIp: .CidrIp, Description: .Description }))'

listExistingRules:          ## Get the existing ingress rules with the specified description
	@aws ec2 describe-security-groups --region ${REGION} --group-ids ${SECURITY_GROUP_ID} | jq -c '.SecurityGroups[0].IpPermissions[] | ({ FromPort: .FromPort, ToPort: .ToPort, IpProtocol: .IpProtocol } + ( .IpRanges[] | select(.Description == ${DESCRIPTION}) | { CidrIp: .CidrIp }))'

addRuleToSecurityGroup:     ## Get current IP and add it to security group
	@./validIp.sh ${CURRENT_IP} && \
	echo ${CURRENT_IP} && \
	aws ec2 authorize-security-group-ingress --region ${REGION} --group-id ${SECURITY_GROUP_ID} \
		--ip-permissions IpProtocol=${IP_PROTOCOL},FromPort=${PORT},ToPort=${PORT},IpRanges='[{ CidrIp=${CURRENT_IP}/32,Description=${DESCRIPTION} }]' | cat

deleteExistingRules:        ## Remove ingress rule with current description if exists
	@for row in $$(make listExistingRules) ; do \
		echo $${row}; \
		aws ec2 revoke-security-group-ingress --region ${REGION} --group-id ${SECURITY_GROUP_ID} --cli-input-json $${row} | cat; \
	done

showIP:                     ## Get your current IP from AWS and print it
	@echo ${CURRENT_IP}

updateIp:                   ## Delete Security group rule and add current IP
	@$(MAKE) deleteExistingRules
	@$(MAKE) addRuleToSecurityGroup
