for project in cinetodayrss tests
do
  black $project
  PYTHONPATH=. pylint $project
done
