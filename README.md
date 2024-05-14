# Mutual Aid Scripts

These two scripts allow for the quick calculation of mutual aid distributions, and can also send out emails automatically to a list of contributors.

Scripts expect a `data` directory with the following files.

- `config.py`: a python file containing sensitive configuration information. For now, this includes the expected TF base pay.
- `tfs.py`: a python file containing a dictionary of information about TFs. See the example file `example-tfs.py` for more.
- `everyone.txt`: a TSV list of everyone involved in mutual aid, containing expected contribution amounts and roles. see `example-everyone.txt` for more.
- `confirmations.txt`: a TSV list of contributors, only, to be used for sending out weekly confirmation emails. See `example-confirmations.txt` for more.
- `distributions.txt` a TSV list of distribution assignments, used to send out emails to contributions. See `example-distributions.txt` for more.
- `smtp.conf`: an SMTP configuration file containing authorization info. See `example-smtp.conf`, or see Eli for the actual version.

Note that the output from `run-distribution.py` is basically identical to the `distributions.txt` file, except that the former outputs as a CSV and the latter inputs as a TSV, due to Google Sheets copy-and-paste funny business. We could easily change this to make the files the same.

Note: these files _should actually be TSVs_, or the scripts should be fixed. Be aware because I think my text editor is replacing tabs with spaces. :)

## Workflow

**Early in the week:** send confirmations.

Go into `send-email.py` and select the confirmation function (towards the end of the script):

```python
# func = distribution_emails
func = confirmation_emails
```

Then send the confirmations:
```
$ python3 send_email.py confirmations.txt
```
this should ideally be a command line flag, sorry.

Note that the email scripts require you to manually confirm each email by hitting `RETURN`.

**Middle of the week:** run the distributions.
```
$ python3 run-distribution.py data/everyone.txt
```

Copy-and-paste this output into a sheet (eventually: just make this script create the file `distributions.txt`)

**End of the week:** send distributions out.

Change the function-selector back:
```python
func = distribution_emails
# func = confirmation_emails
```

And run
```
$ python3 send_email.py distributions.txt
```

Again, you will need to confirm each email by pressing `RETURN`.