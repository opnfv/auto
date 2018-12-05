#!/bin/bash
#
# Copyright 2017-2018 Intel Corporation., Tieto
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script for graphical representation of AUTO result summaries
#
# Usage:
#   ./create_graph [directory]
#
# where:
#       "directory" is an optional directory name, where summary of auto
#       installation report is stored
#       Default value: "$HOME/auto_ci_daily_logs"

NUMBER_OF_RESULTS=50    # max number of recent results to be compared in graph
DIR="$HOME/auto_ci_daily_logs"

function clean_data() {
    rm -rf summary.csv
    rm -rf graph*plot
    rm -rf graph*txt
    rm -rf graph*png
}

function prepare_data() {
    FIRST=1
    CSV_LIST=$(ls -1 ${DIR}/deploy_summary*csv | tail -n ${NUMBER_OF_RESULTS})
    for result_file in $CSV_LIST ; do
        tmp_dir=`dirname $result_file`
        TIMESTAMP=`basename $tmp_dir | cut -d'_' -f2-`
        if [ $FIRST -eq 1 ] ; then
            head -n1 $result_file > summary.csv
            FIRST=0
        fi
        tail -n+2 ${result_file} >> summary.csv
    done
}

function plot_data() {
    echo "Created graphs:"
    for TYPE in png txt; do
        for GRAPH in "graph_pods" "graph_tcs" ; do
            OUTPUT="$GRAPH.plot"
            GRAPH_NAME="${GRAPH}.${TYPE}"
            cat > $OUTPUT <<- EOM
set datafile separator ","
set xdata time
set timefmt "%Y%m%d_%H%M%S"
set format x "%m-%d"
set xlabel "date"
set format y "%8.0f"
EOM
            if [ "$TYPE" == "png" ] ; then
                echo 'set term png size 1024,768' >> $OUTPUT
            else
                echo 'set term dumb 100,30' >> $OUTPUT
            fi

            if [ "$GRAPH" == "graph_pods" ] ; then
                echo 'set ylabel "PODs"' >> $OUTPUT
                echo 'set yrange [0:]' >> $OUTPUT
                echo "set title \"ONAP K8S PODs\"" >> $OUTPUT
                COL1=3
                COL2=4
            else
                echo 'set ylabel "testcases"' >> $OUTPUT
                echo 'set yrange [0:]' >> $OUTPUT
                echo "set title \"ONAP Health TestCases\"" >> $OUTPUT
                COL1=5
                COL2=6
            fi

            iter=0
            echo "set output \"$GRAPH_NAME\"" >> $OUTPUT
            echo -n "plot " >> $OUTPUT
            echo $"'summary.csv' using 1:$COL1 with linespoints title columnheader($COL1) \\" >> $OUTPUT
            echo $", 'summary.csv' using 1:$COL2 with linespoints title columnheader($COL2) \\" >> $OUTPUT
            gnuplot $OUTPUT
            echo -e "\t$GRAPH_NAME"
        done
    done
}

#
# Main body
#
clean_data
prepare_data
plot_data
