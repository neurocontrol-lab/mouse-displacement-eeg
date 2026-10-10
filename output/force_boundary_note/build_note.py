from pathlib import Path
import csv
import numpy as np
root=Path(r"C:/Users/satya/OneDrive/Documents/[S. Perdikis] ErrPo EEG of Mouse Movements/ErrpAnalysis/output/force_boundary_note")
def read(name):
 with (root/name).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
D=read("paired_boundary_summary.csv");B=read("boundary_summary.csv");R=read("residual_summary.csv");ret=read("retention.csv");C=read("centring_audit.csv");E=read("erp_metrics.csv")
def val(r,k):return float(r[k])
def fmt(v,d=3):
 x=float(v)
 if x!=0 and abs(x)<10**(-d):
  mant,exp=f"{x:.2e}".split("e")
  return "$"+mant+r"\times10^{"+str(int(exp))+"}$"
 return f"{x:.{d}f}"
def esc(s):return str(s).replace("_",r"\_")
def b(sub,ch,t,v):return next(r for r in B if r["subject"]==sub and r["channel"]==ch and abs(val(r,"boundary")-t)<1e-9 and int(val(r,"condition"))==v)
def tab(h,rows,align=None):
 return "\\begin{center}\\small\\begin{tabular}{"+(align or "l"*len(h))+"}\\toprule\n"+" & ".join(h)+r" \\"+"\n\\midrule\n"+"\n".join(" & ".join(map(str,r))+r" \\" for r in rows)+"\n\\bottomrule\\end{tabular}\\end{center}\n"
def fig(name,caption,height=None):
 size=rf"width=\linewidth,height={height}\textheight,keepaspectratio" if height else r"width=\linewidth"
 return r"\begin{figure}[htbp]\centering\includegraphics["+size+"]{figures/"+name+"}\n\\caption{"+caption+"}\\end{figure}\n"
N=int(sum(val(r,"matchedAll") for r in ret));eligible=int(sum(val(r,"eligible") for r in ret));total=int(sum(val(r,"trialRows") for r in ret))
text=r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=22mm]{geometry}
\usepackage{graphicx,booktabs,amsmath,longtable}
\usepackage[hidelinks]{hyperref}
\setlength{\parindent}{0pt}\setlength{\parskip}{6pt}\emergencystretch=3em
\newcommand{\uv}{\ensuremath{\mu\mathrm{V}}}
\title{FORCe window boundaries and filtering in movement-locked EEG\\[3pt]\large A matched two-participant pilot research note}
\author{Satyam Awasthi}\date{}
\begin{document}\maketitle
\begin{abstract}
Independent one-second FORCe calls can introduce discontinuities when reconstructed windows are joined. We evaluate those boundaries and an offline adaptation: continuous high-pass filtering, one-second cleaning, and low-pass filtering of a three-second segment before cropping. Four conditions separate cleaning and filtering effects. Across 2,562 matched trials, the +0.5~s Cz median jump was 3.778~\uv\ with bandpass-first FORCe and 0.440~\uv\ with split filtering, versus 0.414~\uv\ in the split control. Finite-segment filtering residuals were below $10^{-9}$~\uv, but broader cleaning-related differences remained. This pilot is descriptive; lower boundary steps or changed ERP waveforms do not establish preservation of underlying neural signals or better artifact removal.
\end{abstract}
\section{Questions and scope}
The primary question is whether window joins introduce unusually large changes and whether proposed processing reduces them without leaving broader transitions. The second question concerns short-segment filtering effects within the retained interval. FORCe is optional; practical consequences are evaluated rather than a benefit assumed.
FORCe combines wavelets, independent-component analysis and thresholding \cite{daly}. Empirically calibrated settings are retained. The supplied Graz study discusses responses around 0.4--0.8~s \cite{graz}; the proposed join at +0.5~s intersects that interval.
\section{Methods}
\subsection{Data and four processing conditions}
Both pilot participants (mle01 and spe30), all eligible task recordings, and pre/post/retest sessions are included. Eight-channel EEG is sampled at 500~Hz; Cz and FCz are primary. Movement-locked extraction is $[-1.5,1.5)$~s. The three cleaning windows are $[-1.5,-0.5)$, $[-0.5,0.5)$ and $[0.5,1.5)$~s: movement onset is no longer a join.
Continuous filters are applied separately to valid recording segments. Acquisition-loss markers, nonfinite samples and timestamp gaps create boundaries. The complete three-second interval must lie outside two-second guards at each segment endpoint. This is an existing conservative policy, not a proven settling bound.
Butterworth filters have order four and are applied forward/backward. The upper cutoff remains 20~Hz. The historical bandpass and separate high-/low-pass designs differ, so this evaluates practical pipelines rather than filter order alone.
"""
text+=tab(["ID","Continuous filtering","Three-second processing"],[
["1","1--20 Hz bandpass","No FORCe"],
["2","1--20 Hz bandpass","Three 1 s FORCe calls"],
["3","1 Hz high-pass","Three 1 s FORCe calls; 20 Hz low-pass"],
["4","1 Hz high-pass","No FORCe; 20 Hz low-pass"]],"cll")
text+=r"""
All conditions are cropped to $[-1,1)$~s, baseline-corrected over $[-0.2,0)$~s, and rejected if absolute amplitude exceeds 100~\uv. FORCe failures reject the complete trial; the existing positive 200~\uv\ channel threshold excludes the unresolved interpolation branch. Source decomposition depth remains two, and no thresholds or library behaviour are changed.
Condition 4 is a diagnostic control. Split/rejoin without cleaning is checked for exact sample preservation. Condition 3 is saved before and after low-pass filtering. Main comparisons use trials accepted in all four conditions; separate retention counts document excluded trials.
\subsection{Boundary measurements}
For trial $i$, channel $c$, and boundary $b$,
\[
J_{icb}=|x_{ic}(b)-x_{ic}(b-2~\mathrm{ms})|.
\]
The same measurement at onset ($b=0$) supplies a non-join location. Ordinary changes are absolute adjacent-sample differences in the retained epoch, excluding $\pm50$~ms around $-0.5$, 0 and $+0.5$~s. Each jump's empirical percentile and the fraction at or above the 99th percentile describe rarity, not an artifact label or formal significance. Percentiles are condition-specific; low-pass filtering changes the reference distribution.
Define the fixed scale from condition 1:
\[
S_{ic}=Q_{95}(x^{(1)}_{ic})-Q_{5}(x^{(1)}_{ic}),\qquad J^*_{icb}=J_{icb}/S_{ic}.
\]
This imposes no Gaussian assumption. Degenerate scales are not interpreted. Cz and FCz are primary; each trial's maximum-channel step is supporting information. A maximum is not assembled into a fictitious trial waveform.
\subsection{Residual checks}
A residual is a processing difference, not necessarily an error.
\begin{enumerate}
\item \textbf{Finite-segment filtering:} condition 4 minus continuous high-pass followed by continuous low-pass, after identical crop and baseline. This isolates applying the low-pass to three seconds instead of continuously.
\item \textbf{Injected boundary:} a unit persistent step or a one-sample spike is injected at each join into an otherwise unchanged no-FORCe sequence. By linearity, subtracting injected/uninjected outputs equals filtering the disturbance. Normalisation is by injected amplitude. Short- and long-segment responses use the actual low-pass coefficients and endpoint handling. Synthetic plots are before baseline correction to isolate filtering; real-trial residuals include baseline correction.
\item \textbf{Actual cleaning:} condition 3 minus 4, and condition 2 minus 1. Both include intended artifact removal and potentially unwanted changes; neither estimates neural error.
\end{enumerate}
For real trials, $r_{ic}(t)=[x_A(t)-x_B(t)]/S_{ic}$. Median, 95th percentile and maximum absolute residual are measured in the full epoch, its outer 200~ms at each end, the 0.2--0.9~s response interval, and $\pm50$~ms at both joins. Values are reported in \uv\ and reference-range fractions. No arbitrary cutoff declares a boundary resolved.
A centring audit uses the first three eligible trials per recording. The existing wavelet/SOBI path is reconstructed without rejection or coefficient thresholding. Mean shifts and nonconstant RMS residuals distinguish level changes from broader reconstruction differences; the supplied implementation is not edited.
For each participant/session and channel, displaced-minus-non-displaced averages use identical trials. Extrema and largest-absolute-peak times within 0.2--0.9~s describe waveforms, not validated component latencies.
\subsection{Statistical interpretation}
Two-participant results are descriptive. Time samples are not independent replicates, and trial counts cannot substitute for participant replication. No population-level significance or equivalence claim is made. Filtering may spread abrupt changes \cite{widmann}; cropping cannot remove a join within the retained interval.
\section{Results I: FORCe boundaries}
"""
text+=f"There are {len(ret)} recordings, {total:,} trial rows, {eligible:,} eligible complete intervals, and {N:,} trials accepted by all four conditions.\n"
rr=[]
for sub in ["mle01","spe30","Pooled"]:
 z=ret if sub=="Pooled" else [r for r in ret if r["subject"]==sub]
 rr.append([esc(sub)]+[int(sum(val(r,k) for r in z)) for k in ["eligible","BP_control","BP_FORCe","Split_FORCe","Split_control","matchedAll"]])
text+=tab(["Participant","Eligible","1","2","3","4","Common"],rr,"lrrrrrr")
text+=r"\subsection{Magnitude and rarity}"+"\n"
text+=r"Pooled matched-trial statistics are shown below. $J/S$ is expressed as a percentage. Rare means the fraction of jumps at or above each trial's 99th-percentile ordinary change. Participant-specific summaries appear in the appendix."+"\n"
rr=[]
for ch in ["Cz","FCz"]:
 for boundary in [-.5,.5]:
  for v in range(1,5):
   z=b("Pooled",ch,boundary,v)
   rr.append([ch,f"{boundary:+.1f}",v,fmt(z["medianUV"]),fmt(100*val(z,"medianNorm"),2),fmt(z["p95UV"]),fmt(z["above99Percent"],1)])
text+=tab(["Ch.","Join","ID",r"Median (\uv)",r"$J/S$ (\%)",r"$Q_{95}$ (\uv)",r"Rare (\%)"],rr,"lcrrrrr")
a=b("Pooled","Cz",.5,2);p=b("Pooled","Cz",.5,3);c=b("Pooled","Cz",.5,4)
text+=f"At +0.5~s in Cz, median jumps are {fmt(a['medianUV'])}~\\uv\\ for bandpass-first FORCe and {fmt(p['medianUV'])}~\\uv\\ for split FORCe; the split control is {fmt(c['medianUV'])}~\\uv. Rarity fractions are {fmt(a['above99Percent'],1)}\\% and {fmt(p['above99Percent'],1)}\\% respectively. These are pooled pilot descriptions.\n"
paired=[]
for ch in ["Cz","FCz"]:
 for boundary in [-.5,.5]:
  for contrast in [1,2,3]:
   z=next(r for r in D if r["subject"]=="Pooled" and r["channel"]==ch and abs(val(r,"boundary")-boundary)<1e-9 and int(val(r,"contrast"))==contrast)
   paired.append([ch,f"{boundary:+.1f}",contrast,fmt(z["medianDeltaUV"]),fmt(100*val(z,"medianDeltaNorm"),2),fmt(z["positivePercent"],1)])
text+=r"\clearpage\subsection{Paired boundary effects}"+"\n"
text+=r"Contrast A: condition 2 minus 1 (original FORCe effect). B: condition 3 minus 4 (proposed FORCe effect). C: condition 2 minus 3 (change in FORCe usage). A positive value means a larger jump in the first condition. These are medians of paired differences, not differences between marginal medians."+"\n"
text+=tab(["Ch.","Join","Contrast",r"Median $\Delta J$ (\uv)",r"$\Delta J/S$ (\%)",r"Positive (\%)"],[[r[0],r[1],["A","B","C"][r[2]-1]]+r[3:] for r in paired],"lclrrr")
text+=fig("boundary_distributions.png","Matched-trial distributions of normalised jumps in Cz and FCz; BP denotes bandpass. The denominator is fixed across conditions. Onset and all-eight-channel results are supporting measurements.")
text+=r"\clearpage\subsection{Proposed output before and after low-pass}"+"\n"
pre=[]
for ch in ["Cz","FCz"]:
 for boundary in [-.5,.5]:
  before=b("Pooled",ch,boundary,5);after=b("Pooled",ch,boundary,3)
  pre.append([ch,f"{boundary:+.1f}",fmt(before["medianUV"]),fmt(after["medianUV"]),fmt(before["p95UV"]),fmt(after["p95UV"]),fmt(before["maxUV"]),fmt(after["maxUV"])])
text+=tab(["Ch.","Join",r"Median pre",r"Median post",r"$Q_{95}$ pre",r"$Q_{95}$ post","Max pre","Max post"],pre,"lcrrrrrr")
text+=r"All values are in \uv\ and use the same proposed-cleaning trials before and after the final low-pass. Each maximum can arise from a different trial. The reduction demonstrates attenuation of adjacent-sample changes; it does not establish removal of broader effects."+"\n"

text+=r"\subsection{Representative individual trials}"+"\n"
text+=r"Two examples are selected at the median and 95th-percentile rank of condition 2's Cz normalised jump at +0.5~s. Every overlay uses the same trial and channel. This selection illustrates the reference condition; it is not an average treatment effect."+"\n"
text+=fig("representative_trials.png","Full-epoch and join-detail overlays for representative trials. A smoother trace alone cannot establish preservation of the underlying EEG.")
text+=r"\clearpage\section{Results II: filtering and broader changes}\subsection{Finite-segment filtering and synthetic boundaries}"+"\n"
maxedge=max(val(r,"maxUV") for r in R if int(val(r,"test"))==1)
text+=f"The largest finite-segment filtering residual in the matched Cz/FCz data is {fmt(maxedge,6)}~\\uv\\ anywhere in the retained epoch. This describes the tested extraction length and filter only.\n"
text+=fig("filtering_effects.png","Top: absolute normalised filtering-only residual envelopes across matched trials. Bottom: persistent-step and one-sample-spike responses normalised by injected amplitude. A smoothed persistent step still retains a level change; short-minus-long filtering isolates endpoint effects.")
text+=r"\subsection{Response-interval residuals}"+"\n"
text+=r"Contrast 1: finite-segment filtering. Contrast 2: split FORCe minus its control. Contrast 3: bandpass FORCe minus its control. Each entry is the median across trials of the stated within-trial statistic in 0.2--0.9~s; the final column is not a pooled percentile."+"\n"
rr=[]
for test in [1,2,3]:
 for ch in ["Cz","FCz"]:
  z=next(r for r in R if r["subject"]=="Pooled" and int(val(r,"test"))==test and r["channel"]==ch and r["window"]=="Response")
  rr.append([test,ch,fmt(z["medianOfMedianUV"],5),fmt(100*val(z,"medianOfMedianNorm"),3),fmt(100*val(z,"medianOfP95Norm"),3)])
text+=tab(["Contrast","Ch.",r"Median (\uv)",r"Median/$S$ (\%)",r"Trial $Q_{95}/S$ (\%)"],rr,"rlrrr")
text+=r"Cleaning residuals contain intended removal as well as possible unwanted changes. The appendix shows condition-difference waveforms and extrema. Changes in the largest peak can reflect a different selected extremum, rather than latency movement of the same physiological component."+"\n"
text+=r"\subsection{Centring and reconstruction audit}"+"\n"
rr=[]
for sub in ["mle01","spe30"]:
 for ch in ["Cz","FCz"]:
  z=[r for r in C if r["subject"]==sub and r["channel"]==ch]
  rr.append([esc(sub),ch,len(z),fmt(np.median([abs(val(r,"reconstructionShiftUV")) for r in z])),fmt(np.median([val(r,"nonconstantRMSUV") for r in z]),6)])
text+=tab(["Participant","Ch.","Windows",r"$|\mathrm{shift}|$ (\uv)",r"Nonconstant RMS (\uv)"],rr,"llrrr")
shift=np.median([abs(val(r,"reconstructionShiftUV")) for r in C]);nonconst=np.median([val(r,"nonconstantRMSUV") for r in C])
text+=f"Median absolute shift is {fmt(shift)}~\\uv; median nonconstant RMS is {fmt(nonconst,6)}~\\uv. Nonconstant RMS values at floating-point resolution are not evidence of mathematically exact zero. The audit does not attribute all FORCe jumps to centring or justify restoring means without review.\n"
text+=r"""\section{Discussion and limits}
The exact split-filter control distinguishes cleaning effects from filtering implementation effects. All four conditions are needed for this attribution even though condition 4 is not a candidate final pipeline.
Three-second extraction provides 0.5~s of additional context beyond each cropped endpoint, but leaves joins at $-0.5$ and $+0.5$~s inside the retained epoch. A low-pass attenuates sharp changes; it need not remove a sustained shift. The synthetic response describes known disturbances, not every real FORCe reconstruction effect.
Individual-trial distributions take priority over averages for the boundary question. Conversely, no-FORCe data are not neural ground truth, and a cleaning residual does not distinguish artifact from neural content. Visual smoothness, rarity, residual size and apparent peak changes must be interpreted together.
The practical result is a strong reduction in sharp boundary steps under the proposed processing, with negligible outer-endpoint filtering effects for this setup. However, median response-interval cleaning residuals remain about 9.5--10.0\% of the reference voltage range in the proposed condition. Those changes cannot be classified as artifact removal or neural distortion from this pilot alone. The pilot does not retune FORCe, benchmark artifact removal, establish classifier performance, or support population-level inference. Retaining FORCe should depend on useful artifact handling without unacceptable response changes. Proceeding without it remains an option.
\clearpage\appendix\section{Participant-specific boundary statistics}
\small\begin{longtable}{llcrrrr}\toprule Participant & Ch. & Join & ID & Median (\uv) & $J/S$ (\%) & Rare (\%)\\\midrule\endhead
"""
for sub in ["mle01","spe30"]:
 for ch in ["Cz","FCz"]:
  for boundary in [-.5,.5]:
   for v in range(1,5):
    z=b(sub,ch,boundary,v)
    text+=" & ".join(map(str,[esc(sub),ch,f"{boundary:+.1f}",v,fmt(z["medianUV"]),fmt(100*val(z,"medianNorm"),2),fmt(z["above99Percent"],1)]))+r" \\"+"\n"
text+=r"\bottomrule\end{longtable}\normalsize" + "\n"
text+=r"\section{Onset and maximum-channel supporting summaries}"+"\n"
support=[]
for ch in ["Cz","FCz","All-eight maximum"]:
 for boundary in ([0] if ch!="All-eight maximum" else [-.5,0,.5]):
  for v in range(1,5):
   z=b("Pooled",ch,boundary,v)
   support.append([ch.replace("All-eight maximum","Max-eight"),f"{boundary:+.1f}",v,fmt(z["medianUV"]),fmt(z["p95UV"]),fmt(z["maxUV"]),fmt(z["above99Percent"],1)])
text+=r"Movement onset is not a join in these conditions. Maximum-channel measurements select each trial's largest raw step, then use that channel's ordinary-change distribution. They can select different channels across conditions."+"\n"
text+=tab(["Channel","Time","ID",r"Median (\uv)",r"$Q_{95}$ (\uv)",r"Max (\uv)",r"Rare (\%)"],support,"lcrrrrr")

text+=r"\clearpage\section{Condition-difference waveforms}"+"\n"
text+=fig("erp_differences_1.png","Matched displaced-minus-non-displaced waveforms for mle01, by session and channel. Joins are at -0.5 and +0.5 s.")
text+=fig("erp_differences_2.png","Matched displaced-minus-non-displaced waveforms for spe30, by session and channel. Joins are at -0.5 and +0.5 s.")
text+=fig("actual_cleaning_residuals.png","Actual cleaning residuals for the same representative trials, in Cz and FCz. Both curves use the common condition-1 voltage scale. These differences include artifact removal and are not neural-error estimates.")
text+=r"\clearpage\section{ERP extrema and peak-time descriptions}\small\begin{longtable}{lllrrrr}\toprule Participant & Session & Ch. & ID & Min (\uv) & Max (\uv) & Peak time (s)\\\midrule\endhead"+"\n"
for r in E:
 text+=" & ".join(map(str,[esc(r["subject"]),r["session"],r["channel"],int(val(r,"condition")),fmt(r["minUV"]),fmt(r["maxUV"]),fmt(r["peakTimeSeconds"])]))+r" \\"+"\n"
text+=r"""\bottomrule\end{longtable}\normalsize
\clearpage\begin{thebibliography}{9}
\bibitem{daly} Daly I, Scherer R, Billinger M, M\"uller-Putz G. FORCe: Fully Online and Automated Artifact Removal for Brain-Computer Interfacing. \emph{IEEE Transactions on Neural Systems and Rehabilitation Engineering}. 2015;23(5):725--736. \href{https://doi.org/10.1109/TNSRE.2014.2346621}{doi:10.1109/TNSRE.2014.2346621}.
\bibitem{graz} Amaunam I, Sultana M, Rodriguez-Herreros B, Tadi T, Leeb R, Perdikis S. EEG correlates of error-related activity during ballistic computer mouse movements. Graz BCI Conference, 2024. Supplied manuscript.
\bibitem{widmann} Widmann A, Schr\"oger E. Filter Effects and Filter Artifacts in the Analysis of Electrophysiological Data. \emph{Frontiers in Psychology}. 2012;3:233. \href{https://doi.org/10.3389/fpsyg.2012.00233}{doi:10.3389/fpsyg.2012.00233}.
\end{thebibliography}\end{document}
"""
(root/"FORCe_boundary_research_note.tex").write_text(text,encoding="utf-8")
print("LaTeX research note source written")
