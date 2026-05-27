#!/bin/bash

# Fix the BAML definition syntax correctly to make it match exactly the accepted BAML syntax 
find /Users/cianmacandeisigh/dev/kings_college_galway/oideachais/baml_src -type f -name "*.baml" -print0 | xargs -0 sed -i '' -E 's/([a-zA-Z_0-9]+):[[:space:]]+(string\??|int\??|float\??|bool\??|CelticLanguage\??|EducationLevel\??|ExamLevel\??|LearningOutcome\[\]\??|DifficultyLevel\??|RelationshipType\??|SkillCategory\??|QuestionType\??|IrishCopulaType\??|MutationType\??|IrishGender\??|IrishDeclension\??|TearmaPartOfSpeech\??|TerminologyDomain\[\]\??|TerminologyDomain\??|TermStatus\??|TerminologySource\??|DataSource\??|MetricCategory\??|AggregationLevel\??|StatisticsQuery\??|SupernaturalType\??)[[:space:]]*@description/\1: \2 @description/g'

# Let's just fix it by ensuring every definition inside a class has the correct colon. The previous perl script probably did some weird stuff. Let's reset BAML to original and patch the functions specifically
