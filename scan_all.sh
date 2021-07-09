#!/bin/bash
show_help () {
	echo "scan all frequencies and retrieve sibs recursively"
	echo ""
	echo "	-b, --band	start band		(default=3)"
	echo "	-g, --gain	rx gain			(default=50)"
	echo "	-a, --args	sdr args		(default='rxant=LNAW')"
	echo "	-t, --timeout	timeout to get SIBs	(default=10)"
	echo "	-s, --start	start earfcn		(default all)"
	echo "	-o, --output				(default=/tmp/srsue_out.json)"
	exit
}

srsue_path="binaries/srsue"
cell_search_path="binaries/cell_search"

band=3
gain=60
args="rxant=LNAW"
timeout=10
start_arfcn=""
out_file="/tmp/srsue_out.json"

while [[ $# -gt 0 ]]; do
  case $1 in
			-b|--band)
			band="$2"
			shift # past argument
			shift # past value
      ;;
			-o|--output)
			out_file="$2"
			shift # past argument
			shift # past value
			;;
			-t|--timeout)
			timeout="$2"
			shift # past argument
			shift # past value
			;;
			-s|--start)
			start_arfcn="$2"
			shift # past argument
			shift # past value
			;;
			-g|--gain)
			gain="$2"
			shift # past argument
			shift # past value
			;;
			*)
      show_help
      exit
      ;;
  esac
done


first_done=0

if [[ ! -z "$start_arfcn" ]]; then
	start_arfcn=" -s $start_arfcn"
fi

arfcn_list=()

do_scan () {
	echo "checking $1"
	arfcn_list[${#arfcn_list[*]}]=$1
	./$srsue_path srsue/ue.conf.example --expert.lte_sample_rates=true --rf.device_args "$args" --rat.eutra.dl_earfcn $1 --ue.timeout $timeout| tee /tmp/srsue_out
	data=$(</tmp/srsue_out)
	cell_info=$(echo $data |jq --slurp |jq --arg earfcn "$1" '{"earfcn":$earfcn,"sysblocks":.}'|jq --slurp)
	echo $cell_info | jq
	cat $out_file|jq
	data=$(<$out_file)
	echo $data |jq --argjson cell "$cell_info" '. += [$cell]' > $out_file
	if [[ -f "/tmp/srsue_sibs_acquired/$1/5.json" ]]; then
		for cell in $(cat "/tmp/srsue_sibs_acquired/$1/5.json"|jq ".sib5.interFreqCarrierFreqList"|jq -c '.[]'); do
			next_arfcn=$(echo $cell | jq '."dl-CarrierFreq"')
			if [[ ! ${arfcn_list[@]} == *"$next_earfcn"* ]]; then
				echo $next_arfcn" not in arfn arr "${arfcn_list[@]}
		    do_scan $next_arfcn
			fi
		done
	fi
}


while [[ $first_done -eq 0 ]]; do
	earfcn=$(./$cell_search_path -a "$args" -g $gain -b $band $start_arfcn)
	if [[ $earfcn == "" ]]; then
		echo "[ Err ] Can't found any cell on band $band. Maybe try another one?"
		exit
	fi
	arfcn_list[${#arfcn_list[*]}]=$earfcn
	echo "Setting first earfcn to $earfcn"

	mkdir -p	"/tmp/srsue_sibs_acquired"
	./$srsue_path srsue/ue.conf.example --expert.lte_sample_rates=true --rf.device_args "$args" --rat.eutra.dl_earfcn $earfcn --ue.timeout $timeout| tee /tmp/srsue_out
	data=$(</tmp/srsue_out)
	if [[ $data != *"[-] can't decode SIBs after 10 seconds, shutting down"* ]]; then
	  first_done=1
		echo $data |jq --slurp |jq --arg earfcn "$earfcn" '{"earfcn":$earfcn,"sysblocks":.}'|jq --slurp > $out_file
		break
	fi
	earfcn=$(($earfcn+1))
	start_arfcn="-s $earfcn"
done

cat $out_file | jq
echo $earfcn

if [[ -f "/tmp/srsue_sibs_acquired/$earfcn/5.json" ]]; then
	for cell in $(cat "/tmp/srsue_sibs_acquired/$earfcn/5.json"|jq ".sib5.interFreqCarrierFreqList"|jq -c '.[]'); do
		echo "arfcn arr: "${arfcn_list[@]}
		next_arfcn=$(echo $cell | jq '."dl-CarrierFreq"')
		echo $next_arfcn
		if [[ ! ${arfcn_list[@]} == $next_earfcn ]]; then
			echo $next_arfcn" not in arfn arr "${arfcn_list[@]}
	    do_scan $next_arfcn
		fi
	done
fi
