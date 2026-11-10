"""Describe jump- and steering-aligned waveforms and endpoint-distance associations."""

from collections import Counter, defaultdict
import csv
import gzip
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if p.name == "Code")))
from research_paths import result_path
from helpers.erp_report_encoding import pack_waveforms
from prepare_steering_trials import rows, write


SUBSETS = ("all", "late", "not_detected")
CONTROL_NAMES = ("No early steering", "Later steering", "No steering detected")
DISTANCES = {
    "full_log_min_distance_px": "Full eligible log (primary)",
    "closest_distance_px": "Closest during outward reach",
    "endpoint_distance_px": "Manuscript endpoint",
}
CHANNEL_COLORS = ("#53657a", "#137f6a", "#27232b")


def pool(sums, counts):
    numerator = sums.sum(axis=-1)
    n = counts.sum(axis=-1)
    return np.divide(numerator, n, out=np.full_like(numerator, np.nan), where=n > 0)


def panel(ax, time, channel):
    ax.axvline(0, color="#53657a", lw=.8, ls=":")
    ax.axhline(0, color=".75", lw=.6)
    ax.set(xlim=(time[0], time[-1]+2), title=channel)
    ax.spines[["top", "right"]].set_visible(False)


def finish(fig, path, handles=None, labels=None, xlabel="Time from event (ms)"):
    fig.supxlabel(xlabel)
    fig.supylabel("Amplitude (µV)")
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=len(labels), frameon=False,
                   bbox_to_anchor=(.5,.04))
    fig.tight_layout(rect=(.01,.08,1,.96))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_pairs(out, d, channels, nonpilot):
    means = pool(d["jumpSum"], d["pairCounts"][None,None,None,:,:,:])
    time = d["jumpMs"]
    def cohort(g):
        use = nonpilot & (d["pairCounts"][g].sum(axis=-1)>0)
        return means[:,:,:,g][:,:, :,use].mean(axis=-1)
    pooled = cohort(0)
    fig, axes = plt.subplots(2,4,figsize=(12.8,6.2),sharex=True,sharey=True)
    fig.suptitle("Early steering versus no early steering · jump-aligned matched D trials")
    for c, (ax, channel) in enumerate(zip(axes.flat, channels)):
        control, early = pooled[:,c,:].T
        handles = ax.plot(time,np.column_stack([control,early,early-control]),lw=1.35)
        for line, color in zip(handles,CHANNEL_COLORS):
            line.set_color(color)
        panel(ax,time,channel)
        ax.axvline(250,color=".75",lw=.8,ls=":")
    finish(fig,out/"jump_early_steering.png",handles,
           [CONTROL_NAMES[0],"Early steering","Early minus no early steering"],"Time from jump (ms)")

    later, none = cohort(1), cohort(2)
    fig, axes = plt.subplots(2,4,figsize=(12.8,6.2),sharex=True,sharey=True)
    fig.suptitle("Jump-aligned matched differences by control group")
    for c,(ax,channel) in enumerate(zip(axes.flat,channels)):
        handles=ax.plot(time,np.column_stack([later[:,c,1]-later[:,c,0],none[:,c,1]-none[:,c,0]]),lw=1.4)
        panel(ax,time,channel)
    finish(fig,out/"jump_control_subsets.png",handles,
           ["Early minus later steering","Early minus no detection"],"Time from jump (ms)")


def plot_alignment(out, d, channels, nonpilot, detected):
    use = nonpilot & (d["steerCounts"].sum(axis=-1)>0)
    counts = d["steerCounts"][None,None,:,:]
    time = [d["jumpMs"],d["steerMs"]]
    means = [pool(d[k], counts)[:,:,use].mean(axis=-1) for k in ("steerJumpSum","steerSum")]
    delays = [float(r["steering_ms_from_jump"]) for r in detected if r["cohort"] != "pilot"]
    low, median, high = np.percentile(delays,[5,50,95])
    fig, axes = plt.subplots(4,4,figsize=(13.6,10.2),sharex="col")
    fig.suptitle("The same detected-steering reaches aligned to the jump and steering")
    for c, channel in enumerate(channels):
        row, col = divmod(c,2)
        amp = 1.08*max(abs(x[:,c]).max() for x in means)
        for i, (name, limits) in enumerate((
            ("Jump", (low, median, high)), ("Steering", (-high, -median, -low)),
        )):
            ax=axes[row,2*col+i]
            ax.axvspan(limits[0],limits[2],color="#ffedcb",zorder=0)
            ax.axvline(limits[1],color="#a85416",lw=.8,ls="--")
            ax.plot(time[i],means[i][:,c],color="#1864a4",lw=1.35)
            panel(ax,time[i],f"{channel} · {name}")
            ax.set_ylim(-amp,amp)
    finish(fig,out/"jump_and_steering_alignment.png")
    return low, median, high


def window_metadata(window):
    return dict(component_window=window["component_window"], electrodes="/".join(window["electrodes"]),
                start_ms=window["start_ms"], end_ms_exclusive=window["end_ms_exclusive"])


def describe_pairs(out, d, windows, cohorts):
    groups = []
    counts = d["pairCounts"]
    for g, control in enumerate(SUBSETS):
        for p, subject in enumerate(d["subjects"]):
            for s, session in enumerate(d["sessions"]):
                n = int(counts[g,p,s])
                if not n:
                    continue
                for win in windows:
                    samples=(d["jumpMs"]>=win["start_ms"]) & (d["jumpMs"]<win["end_ms_exclusive"])
                    electrodes=[list(d["channels"]).index(ch) for ch in win["electrodes"]]
                    trace=d["jumpSum"][:,:,:,g,p,s]
                    control_uv, early_uv=trace[samples][:,electrodes,:].mean(axis=(0,1))/n
                    groups.append(dict(subject=subject, session=session, cohort=cohorts[subject],
                                       control_group=control, **window_metadata(win), pairs=n,
                                       control_uv=control_uv, early_uv=early_uv, difference_uv=early_uv-control_uv))
    write(out/"steering_contrast_by_session.csv", groups)

    pooled = defaultdict(list)
    for row in groups:
        if row["cohort"] != "pilot":
            key = row["control_group"], row["component_window"]
            pooled[key].append(row)
    result=[]
    for (control, name), values in pooled.items():
        individuals=defaultdict(list)
        for row in values:
            individuals[row["subject"]].append(row)
        diffs=np.array([np.average([v["difference_uv"] for v in vals],weights=[v["pairs"] for v in vals])
                        for vals in individuals.values()])
        spec=next(w for w in windows if w["component_window"]==name)
        result.append(dict(control_group=control, **window_metadata(spec), participants=len(diffs),
                           pairs=sum(r["pairs"] for r in values), mean_difference_uv=diffs.mean(),
                           median_difference_uv=np.median(diffs), positive_participants=int((diffs>0).sum())))
    write(out/"steering_contrast_summary.csv",result)
    return result


def endpoint_associations(out, trial_rows, features, windows):
    """Separate within-run, within-side distance slopes, adjusted for RT and jump delay."""
    eligible = defaultdict(list)
    for i,r in enumerate(trial_rows):
        if r["distance_eligible"] == "1":
            eligible[r["subject"]].append(i)
    results = []
    for subject, indices in sorted(eligible.items()):
        group=[trial_rows[i] for i in indices]
        if len(group)<10:
            continue
        strata=defaultdict(list)
        for i,r in enumerate(group):
            strata[r["run"],r["side"]].append(i)
        y=features[indices].copy()
        for key in DISTANCES:
            x=np.array([[float(r[key])/100,float(r["reaction_ms"])/100,
                         2*float(r["jump_delay_samples"])/100] for r in group])
            centered_y=y.copy()
            for loc in strata.values():
                x[loc]-=x[loc].mean(axis=0)
                centered_y[loc]-=centered_y[loc].mean(axis=0)
            coef, _, rank, _=np.linalg.lstsq(x,centered_y,rcond=None)
            if rank<3:
                continue
            for w,window in enumerate(windows):
                results.append(dict(subject=subject,cohort=group[0]["cohort"],trials=len(group),
                                    distance=key,**window_metadata(window), slope_uv_per_100px=coef[0,w]))
    write(out/"endpoint_distance_slopes.csv",results)
    summary = []
    for key in DISTANCES:
        for win in windows:
            values=np.array([r["slope_uv_per_100px"] for r in results
                             if r["distance"]==key and r["component_window"]==win["component_window"]
                             and r["cohort"]!="pilot"])
            summary.append(dict(distance=key,**window_metadata(win),participants=len(values),
                                mean_slope_uv_per_100px=values.mean(),median_slope_uv_per_100px=np.median(values),
                                p10_slope_uv_per_100px=np.percentile(values,10),
                                p90_slope_uv_per_100px=np.percentile(values,90)))
    write(out/"endpoint_distance_summary.csv",summary)

    fig, axes=plt.subplots(1,3,figsize=(14.5,4.7),sharex=True,sharey=True)
    names=[w["component_window"] for w in windows]
    for ax, (key, label) in zip(axes, DISTANCES.items()):
        ax.axvline(0,color=".55",lw=.8,ls=":")
        for j,name in enumerate(names):
            values=[r["slope_uv_per_100px"] for r in results
                    if r["distance"]==key and r["component_window"]==name and r["cohort"]!="pilot"]
            ax.scatter(values,np.full(len(values),j),s=17,alpha=.65,color="#1864a4")
            ax.scatter(np.median(values),j,s=40,color="#27232b",marker="D",zorder=3)
        ax.set(yticks=np.arange(len(names)),yticklabels=names,title=label)
        ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Descriptive distance slopes across non-pilot participants · diamonds show medians")
    fig.supxlabel("Amplitude change (µV per 100 px farther from target)")
    fig.tight_layout()
    fig.savefig(out/"distance_associations.png",dpi=150)
    plt.close(fig)
    return summary


def save_report_means(out, data, cohorts, detected):
    """Save ERP_02 waveform selections by participant and session."""
    counts = data["pairCounts"]
    aligned_counts = data["steerCounts"][None, :, :]
    waveforms = {"pairs": pack_waveforms(data["jumpMs"], data["jumpSum"], counts)}
    for name, time, field in (
        ("detected_jump", "jumpMs", "steerJumpSum"), ("detected_steering", "steerMs", "steerSum"),
    ):
        descriptor = pack_waveforms(data[time], data[field][:, :, None, None, :, :], aligned_counts)
        descriptor.update(classes=1, subsets=1, counts=aligned_counts.transpose(1, 2, 0).astype(int).tolist())
        waveforms[name] = descriptor
    delays = defaultdict(list)
    for row in detected:
        for scope in (row["subject"], row["cohort"]):
            for session in (row["session"], "all"):
                delays[f"{scope}|{session}"].append(float(row["steering_ms_from_jump"]))
    delay_ranges = {key: np.percentile(values, [5, 50, 95]).tolist() for key, values in delays.items()}
    payload = dict(
        subjects=list(data["subjects"]), sessions=list(data["sessions"]), channels=list(data["channels"]),
        cohorts=cohorts, counts=counts.transpose(1, 2, 0).astype(int).tolist(), waveforms=waveforms,
        delay_ranges=delay_ranges,
    )
    (out / "waveform_means.json").write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


def main():
    out=result_path("ERP_02")
    d=loadmat(out/"tmp"/"waveform_sums.mat",simplify_cells=True)
    trial_rows=rows(out/"trial_selection.csv")
    pairs=rows(out/"steering_pairs.csv")
    windows=json.loads((out/"windows.json").read_text(encoding="utf-8"))
    assert d["features"].shape==(len(trial_rows),len(windows))
    assert d["pairCounts"][0].sum()==len(pairs)
    cohorts={r["subject"]:r["cohort"] for r in trial_rows}
    nonpilot=np.array([cohorts[s]!="pilot" for s in d["subjects"]])
    detected=[r for r in trial_rows if r["steering_eeg_eligible"]=="1"]
    assert len(detected)==d["steerCounts"].sum()
    plot_pairs(out,d,d["channels"],nonpilot)
    delay_quantiles=plot_alignment(out,d,d["channels"],nonpilot,detected)
    save_report_means(out, d, cohorts, detected)
    contrasts=describe_pairs(out,d,windows,cohorts)
    observed = rows(result_path("AUD_02") / "target_boundary/observed_hit_trials.csv.gz")
    minima = {(r["run"], r["trial"]): float(r["full_log_min_distance_px"])
              for r in observed if r["condition"] == "D"}
    assert len(minima) == len(trial_rows)
    for row in trial_rows:
        row["full_log_min_distance_px"] = minima[row["run"], row["trial"]]
    slopes=endpoint_associations(out,trial_rows,d["features"],windows)
    with gzip.open(out/"trial_window_amplitudes.csv.gz","wt",encoding="utf-8",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["run","trial",*[w["component_window"]+" (µV)" for w in windows]])
        writer.writerows([r["run"],r["trial"],*features.round(9)] for r,features in zip(trial_rows,d["features"]))

    coverage=defaultdict(Counter)
    for r in trial_rows:
        key=r["subject"],r["session"]
        coverage[key].update(["accepted_D", "window_"+r["steering_250"]])
        coverage[key]["steering_aligned"]+=int(r["steering_eeg_eligible"])
        coverage[key]["distance_eligible"]+=int(r["distance_eligible"])
    for p in pairs:
        coverage[p["subject"],p["session"]].update(["pairs","control_"+p["control_group"]])
    fields=sorted({k for c in coverage.values() for k in c})
    write(out/"coverage_by_session.csv",[dict(subject=s,session=v,cohort=cohorts[s],
          **{k:c[k] for k in fields}) for (s,v),c in sorted(coverage.items())])
    print("Matched controls:",dict(Counter(p["control_group"] for p in pairs)))
    print("Match median absolute gaps, RT / jump delay:",
          [np.median([abs(int(p[key])) for p in pairs]) for key in ("reaction_gap_ms","jump_delay_gap_ms")])
    print("Aligned:",len(detected),"detected total:",sum(bool(r["steering_ms_from_jump"]) for r in trial_rows))
    print("Steering delays (non-pilot p05/median/p95):", np.round(delay_quantiles,1))
    print("Distance eligible:",sum(int(r["distance_eligible"]) for r in trial_rows))
    for name in ("Interaction negativity","Posterior positivity"):
        print(name,[r for r in contrasts if r["component_window"]==name and r["control_group"]=="all"])
        print(name,[r for r in slopes if r["component_window"]==name])


if __name__ == "__main__":
    main()
