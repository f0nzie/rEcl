## Test environments for rEcl 0.1.9
* local Windows 10 64-bit, R 3.5.3       0 errors v | 0 warnings v | 0 notes v
* Debian 9, R 3.5.3                      0 errors v | 0 warnings v | 0 notes v
* win-builder (devel and release)        Status: 1 NOTE
    Possibly mis-spelled words in DESCRIPTION:
    Konstantin (13:8)
    Sermyagin (13:19)

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

Well, python is probably installed oon all check machines, hence it 
would be good to use these in the checks.
Nevertheless, you have to declare in the `SystemRequirements` field that 
Python is needed.
Please fix and resubmit.
Best,
Uwe Ligges

> In the case of rEcl I call a Python Anaconda environment.
> (3) I will fix the software name **Eclipse** to single quotes. Thanks.
