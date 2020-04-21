#!/bin/bash

LOG_DIR="logs"
mkdir -p $LOG_DIR

DUMP_DIR="/hdd1/miyoung/covidAsk/dumps/denspi_2020-04-10"
Q_PORT_NQ="9011"
D_PORT_NQ="9021"
PORT_NQ="9031"

# Serve query encoder / metadata / phrase dump
nohup python covidask.py --run_mode "q_serve" --parallel --cuda --query_encoder_path "/hdd1/miyoung/covidAsk/models/denspi-nq/1/model.pt" --query_port "$Q_PORT_NQ" > "$LOG_DIR/q_serve_$Q_PORT_NQ.log" &
nohup python covidask.py --run_mode "p_serve" --dump_dir "$DUMP_DIR" --query_port "$Q_PORT_NQ" --doc_port "$D_PORT_NQ" --index_port "$PORT_NQ" > "$LOG_DIR/p_serve_$PORT_NQ.log" &
nohup python covidask.py --run_mode "d_serve" --dump_dir "$DUMP_DIR" --doc_ranker_name "COVID-abs-v1-ner-norm-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz" --doc_port "$D_PORT_NQ" > "$LOG_DIR/d_serve_$D_PORT_NQ.log" &

echo "Serving covidAsk. Will take a minute."
