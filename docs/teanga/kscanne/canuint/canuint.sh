#!/bin/bash
alltokens.pl "-‐" "0-9ʼ’'" | perl canuint.pl $@
