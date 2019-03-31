## Test environments
* local OS X install, R 3.5.3
* ubuntu 14.04 (on travis-ci), R 3.5.3
* win-builder (devel and release)

## R CMD check results

0 errors | 0 warnings | 1 note

* This is a new release.


On 29.03.2019 17:54, Alfonso.Reyes@OilGainsAnalytics.com wrote:
> Hello Svetlana,
> (1) I quoted the name  **Konstantin Sermyagin** because R build was
> throwing warnings. I will try again removing the quotes. Is it acceptable
> to CRAN a warning about the first and last name of an author?

Yes, false positives in the spell checks are expected, hence sinmply 
write names as they are.

> (2) The examples are wrapped in *\dontrun{}* because the functions call
> Python.
> I read in the CRAN tutorial to use \dontrun{} for the cases where the
> developer is including an external library or software.

Well, python is probably installed oon all check machines, ehnce it 
would be good to use these in the checks.
Nevertheless, you have to declare in the SystemRequirements field that 
Python is needed.
Please fix and resubmit.
Best,
Uwe Ligges

> In the case of rEcl I call a Python Anaconda environment.
> (3) I will fix the software name **Eclipse** to single quotes. Thanks.
