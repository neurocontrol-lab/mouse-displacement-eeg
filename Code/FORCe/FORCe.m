function [cleanEEG, diagnostics] = FORCe( EEGdata, Fs, chanLocs, useAcc )
    % Update by Satyam: optional cleaning diagnostics; fixed source depth of two.
    % Existing four-input, one-output calls remain valid.
    %
    % FORCe -- changed name for confilct with another toolbox 
    %
    %   Fully automated and Online artifact Removal for brain-Computer
    %   interfacing.
    %
    % First perform hard threhsolding to reject very high amplitude
    % channels. Then re-reference, calculate wavelet coefficients,
    % estimate (via SOBI) ICA de-mixing matrix, extract features, apply
    % thresholds. Flag ICs for inclusion or exclusion, soft threshold
    % spikes and reconstruct cleaned signals.
    %
    % Inputs:
    %
    %   EEGdata     - M x N matrix of M channels by N samples. Note, the
    %           window length is supplied by the caller (pipeline: 2 s).
    %   accSigs     - Signals from the accelerometer (currently not fully
    %           tests; the acceleromter didn't work when attempting to
    %           acquire test signals).
    %   Fs          - sampling rate (note, only tested with 512 Hz so far,
    %           some parts may expect this).
    %   chanLocs    - Locations of the channels used in EEGlab format.
    %   useAcc      - 0 = don't use, 1 = use (I suggest setting to zero
    %           until someone has implemented and tested this part).
    %
    % Output:
    %
    %   cleanEEG    - cleaned EEG with the same dimensions as EEGdata.
    %
    % Author: Ian Daly, 2013
    %
    % License:
    %
    % This program is free software; you can redistribute it and/or modify it under
    % the terms of the GNU General Public License as published by the Free Software
    % Foundation; either version 2 of the License, or (at your option) any later
    % version.
    %
    % This program is distributed in the hope that it will be useful, but WITHOUT
    % ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
    % FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
    %
    % You should have received a copy of the GNU General Public License along with
    % this program; if not, write to the Free Software Foundation, Inc., 59 Temple
    % Place - Suite 330, Boston, MA  02111-1307, USA.
    %
    %
    % REFERENCES:
    %
    % Please cite the following manuscript when using this method.
    %
    % Daly, I. et al., 2014. FORCe: Fully Online and automated artifact 
    %   Removal for brain-Computer interfacing. IEEE transactions on neural
    %   systems and rehabilitation engineering : a publication of the IEEE 
    %   Engineering in Medicine and Biology Society. Available at: 
    %   http://www.ncbi.nlm.nih.gov/pubmed/25134085
    %
    %
    %**********************************************************************
       
    % Begin function proper, check the dimmensions of the input data.   
    % Update by Satyam: initialize diagnostics without changing cleaning decisions.
    diagnostics = struct('status','ok','removedChannels',[], ...
        'removedICs',[],'allICsRemoved',false);
    % Update by Satyam: restore fixed depth; unsupported accelerometer mode fails clearly.
    level = 2;
    assert(useAcc == 0,'FORCe:UnsupportedAccelerometer','Accelerometer mode is unsupported');
    N = size( EEGdata,1 );
    M = size( EEGdata,2 );
    
    % Check for NaNs and Infs, if found display warning.
    for chNo = 1:N,
        if any( isnan( EEGdata(chNo,:) ) ),
            disp( 'Warning: signal contains NaNs' );
        end
        if any( isinf( EEGdata(chNo,:) ) ),
            disp( 'Warning: signal contains Infs' );
        end
    end
    
    % Step 1. Hard threshold channels for extreme values (> 200uV).
    remCh = [];
    for chNo = 1:N,
        if max( EEGdata(chNo,:) ) > 200,
            remCh = [remCh chNo];
        end
    end
    
    % Check we have some usable data (ie. there are some channels with
    % amplitude below the 200uV threshold). If no usable date found just
    % retunr what we have (ie. retunr input without cleaning).
    % Update by Satyam: expose channels rejected by the original threshold.
    diagnostics.removedChannels = remCh;
    if length( unique( remCh ) ) == size( EEGdata,1 ),
        % Update by Satyam: distinguish aborted cleaning from successful output.
        diagnostics.status = 'no_usable_channels';
        disp( 'Error: No usable data in this EEG epoch: aborting!' );
        cleanEEG = EEGdata;
        return;
    end
    
    % Identify channels in frontal locations ...
    frontChans = [];
    for chNo = 1:length( chanLocs ),
        if length( strfind( chanLocs(chNo).labels, 'F' ) ) > 0,
            frontChans = [frontChans chNo];
        end
    end

  
    % ... and other locations.
 
    % otherChans = setdiff( 1:16,frontChans ); %%
    NCh = length( chanLocs );
    otherChans = setdiff( 1:NCh,frontChans );
   
    % Estimate the new scalp data from the old minus removed channels.
    chData = estimateRemovedChs( EEGdata,remCh,chanLocs );
    
    % Estimate wavelet coefficients and ICs via Smlet wavelets and SOBI.
    [ICs mixMat wavePacks] = applyOnlineICAmethodWaveNowsobi( chData );
    wavePacksOut = wavePacks;
    tNodes = get( wavePacks{1},'tN' );
    
    % Update by Satyam: identify the all-lowpass terminal node by its tree index.
    approxBranch = find(tNodes == 2^level-1);
    assert(isscalar(approxBranch),'FORCe:ApproximationNode','Missing approximation node');
    tUse = 1:length( tNodes );
        
    % Step through the terminal nodes.
    for tN = 1:length( tUse ),
        
        % Step 4(a). Extract features relevent to acceleromter measures.
        if useAcc == 1,
            [featsAcc sigsAcc] = getFeaturesAcc( ICs{tUse(tN)},accSigs,Fs );
        else
            featsAcc = [];
            sigsAcc = [];
        end
        
        if tN == approxBranch,% If this is the first terminal node (the approximation coefficients).
            
            % Extract features to be thresholded.
            clear temp;
            remICsPF = [];
            remICsP2P = [];
            
            % For each IC (estiamted from SOBI ICA).
            for iNo = 1:size( ICs{tUse(tN)},1 ),
                % Estimate the IC projection onto the scalp.
                ICtemp = ICs{tUse(tN)};
                for iT = 1:size( ICtemp,1 ),
                    if iT ~= iNo,
                        ICtemp(iT,:) = zeros(1,size(ICtemp,2));
                    end
                end
                projIC{iNo} = mixMat{tUse(tN)} * ICtemp;
                
                % Check the projections of each IC against some
                % simple thresholds.
                for pNo = 1:size( projIC{iNo},1 ),
                    % check thresholds, does the amplitude of the
                    % projection exceed 100uV.
                    passFail(pNo) = checkThresholds(projIC{iNo}(pNo,:));
                    % Check the peak to peak distance between maxima and
                    % minima amplitudes.
                    p2p(pNo) = max( projIC{iNo}(pNo,:) ) - min( projIC{iNo}(pNo,:) );
                end
                % If any ampltudes exceed this threshold mark the
                % corresponding IC fro removal.
                if any( passFail == 0 ),
                    remICsPF = [remICsPF iNo];
                end
                % Same for p2p
                if any( p2p > 60 ),
                    remICsP2P = [remICsP2P iNo];
                end
               
                % Get kurtosis values over projections
                ent(iNo) = mean( kurtosis( projIC{iNo}' ) );
                
                % Check PSDs.
                clear ps;
                clear ps2;
                for pNo = 1:size( projIC{iNo},1 ),
                    % Get power spectrum
                    psT = powerspectrum( projIC{iNo}(pNo,:)',Fs );
                    
                    % Update by Satyam: undefined spectral features must not silently pass.
                    assert(any(psT(1,:)>30) && max(psT(2,2:end))>0, ...
                        'FORCe:InvalidFeature','Undefined spectral feature');
                    % Match to 1/f distribution.
                    clear idealDistro;
                    idealDistro(1,:) = psT(1,:);
                    idealDistro(2,2:end) = 1./psT(1,2:end);
                    % Match to magnitude of other distros (normalise both).
                    idealDistro(2,2:end) = idealDistro(2,2:end) ./ max( idealDistro(2,2:end) );
                    psCheck = psT(2,2:end) ./ max( psT(2,2:end) );
                    % Calc. euclidean distance between ideal (1/F) spectra
                    % and measured spectra.
                    diff = psCheck - idealDistro(2,2:end);
                    specDistT(pNo) = sqrt( diff * diff' );
                    gammaPSDT(pNo) = mean( psT(2,find(psT(1,:) > 30 )) );
                    
                end
                % Take mean distance over projects.
                specDist(iNo) = mean(specDistT);
                % Maximum PSD in gamma and above bands.
                [gammaPSD(iNo),~] = max( gammaPSDT );
                
                % Check stds of projections of ICs.
                for pNo = 1:size( projIC{iNo},1 ),
                    stdProjT(pNo) = std( projIC{iNo}(pNo,:) );
                end
                stdProj(iNo) = max( stdProjT );
                
                % Check std and std ratio (frontal channels / other channels)
                for pNo = 1:size( projIC{iNo},1 ),
                    stdValueT(pNo) = std( projIC{iNo}(pNo,:) );
                end
                stdRatio(iNo) = mean( stdValueT(frontChans) ) / mean( stdValueT(otherChans ) );
                
                % Calculate AMI of each IC.
                featsClust(iNo,:) = extractFeaturesMultiChsWaveAMI( projIC{iNo},Fs );
                
            end
            
             % Update by Satyam: reject undefined IC features through the adapter's failure path.
             assert(all(isfinite([ent specDist gammaPSD stdProj stdRatio featsClust(:)'])), ...
                 'FORCe:InvalidFeature','Nonfinite IC feature');
             % Threshold Std ratio.
             stdRatioRem = find( stdRatio > (mean(stdRatio)+(1*std(stdRatio))) );
             
             % Threshold Gamma rem.
             gammaRem = find( gammaPSD > 1.7 );
             
             % Check spikeness of data.
             if tN == approxBranch,
                 for iNo = 1:size( ICs{tN},1 ),
                     % Find spike zones in data.
                     % Update by Satyam: inspect this IC rather than the first IC.
                     muSig = abs( mean( projIC{iNo} ) );
                     A1 = find( muSig(2:end-1) > muSig(3:end) )+1;
                     spikePos = A1(find( muSig(A1) > muSig(A1-1) ));
                     % Calculate coefficients of variation for each spike zone.
                     coefVar = zeros(1,length(spikePos));
                     for i = 1:length( spikePos ),
                         % Update by Satyam: retain current-IC indexing, restore the source's
                         % single-channel denominator pending scientific clarification.
                         zone = abs(mean(projIC{iNo}(:,spikePos(i)-1:spikePos(i)+1),1));
                         coefVar(i) = std(zone) / mean(abs(mean(projIC{iNo}(iNo,spikePos(i)-1:spikePos(i)+1))));
                         assert(isfinite(coefVar(i)),'FORCe:InvalidFeature','Undefined IC spike statistic');
                     end
                     % Apply soft thresholding to any spike zone for which the
                     % coefficient of variation exceeds the threshold.
                     T = 0.1 * (mean(coefVar)+std(coefVar));
                     if length( coefVar ) > 0,
                         noSpikes(iNo) = length( find( coefVar > T ) ) / length( coefVar );
                     else
                         noSpikes(iNo) = 0;
                     end
                 end
                 remNoSpikes = find( noSpikes >= 0.25 );
             end
             
             % Threshold the kurtosis values
             remICsKurt = [];
             for i = 1:length( ent ),
                if ent(i) > mean((ent)) + (0.5*std((ent))) || ent(i) < mean(ent) - (0.5*std(ent)),
                    remICsKurt = [remICsKurt i];
                end
             end
             
             % Threshold the distance to the 1/F distribution.
             rems1F = find( specDist > 3.5 );
             
             % Theshold the ratio of PSDs between < 20Hz and > 20Hz.
             for i = 1:size( ICs{tN},1 ),
                ps = powerspectrum( ICs{tN}(i,:)',Fs );
                muLow = mean(ps(2,find( ps(1,:) < 20 )));
                muHigh = mean(ps(2,find( ps(1,:) > 20 )));
                psRatio(i) = muHigh / muLow;
            end
            % Update by Satyam: empty bands or zero denominators are failures, not passed votes.
            assert(all(isfinite(psRatio)),'FORCe:InvalidFeature','Undefined spectral ratio');
            remICspsRatio = find( psRatio > 1.0 );
            
            % Threshold the std of the IC projects.
            remSTD = find( stdProj > (mean(stdProj)+(2.0*std(stdProj))) );
            
            % Threshold the spikiness (std) of the ICs.
            remSpike = [];
            for i = 1:size( ICs{tN},1 ),
                if max( abs( ICs{tN}(i,:) ) ) > (mean( abs(ICs{tN}(i,:)) ) + (3*std( (ICs{tN}(i,:)) )))
                    remSpike = [remSpike i];
                end
            end
            
            % Threshold the AMI between 2.0 ... 3.0
            remICCs = [find( featsClust > 3 ); find(featsClust < 2.0)]';
            
            % Check which ICs to remove. Remove ICs for which more than 3
            % thresholds are exceeded.
            remICs = ( [gammaRem remICsKurt remICCs remSTD stdRatioRem remICsPF remICsP2P remNoSpikes remICspsRatio remSpike ] );% rems1F  ] ); %  remPSDr  remICCs remSpike  rems1F
    
            % Vote.

            %for iNoType = 1:16,
            for iNoType = 1:NCh,
                lenINo(iNoType) = length( find( remICs == iNoType ) );
            end
            remICs = find( lenINo > 3 );
            
            % Check number of removed ICs is not the same as the total number
            % of ICs.
            % Update by Satyam: expose the original component rejection decisions.
            diagnostics.removedICs = remICs;
            if length( remICs ) == size( ICs{tUse(tN)},1 ),
                % Update by Satyam: flag all-component removal for pipeline QC.
                diagnostics.allICsRemoved = true;
                diagnostics.status = 'all_ics_removed';
                disp( 'Warning: All ICs removed!' );
            end
            
            % Remove the ICs
            keepICs = ICs{tUse(tN)};
            keepICs(remICs,:) = zeros(length(remICs),size(ICs{tUse(tN)},2));
            a = mixMat{tUse(tN)};
            
        end
       
        % If we're currently dealing with the approximation coefficients
        % then remove the ICs flagged by the thresholding above.
        if tN == approxBranch,
            newSigNode{tUse(tN)} = a * keepICs;
        else
            newSigNode{tUse(tN)} = ICs{tUse(tN)};
        end
        
        % Apply soft thresholding to adjust spike magnitudes.
        % Update by Satyam: every non-approximation terminal uses the detail policy.
        if tN ~= approxBranch,
            % Thresholds for detail coefficients.
            checkVal = 0.2;
            adjustVal = 0.07;
        else
            % Thresholds for approximation coefficients.
            checkVal = 0.7;
            adjustVal = 0.8;
        end
        allCoefVar = [];
        clear spikePos;
        clear coefVar;
        for iNo = 1:size( newSigNode{tUse(tN)},1 ),
            
            muSig = newSigNode{tUse(tN)}(iNo,:);
            A1up = find( muSig(2:end-1) > muSig(3:end) )+1;
            A1lo = find( muSig(2:end-1) < muSig(3:end) )+1;
            spikePos{iNo} = [A1up(find( muSig(A1up) > muSig(A1up-1) )) ...
                A1lo(find( muSig(A1lo) < muSig(A1lo-1) ))];
            indUp = find(spikePos{iNo} > 3 );
            indUse = indUp(find( spikePos{iNo}(indUp) < (length(muSig)-2)));
            spikePos{iNo} = spikePos{iNo}( indUse );
            
            % Use wide segments for detection of spike zone coefficients
            % (specifically used +- 3 samples).
            upperVals = var( [newSigNode{tUse(tN)}(iNo,spikePos{iNo}-3); ...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}-2);...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}-1);...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo});...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}+1);...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}+2);...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}+3)] );
            lowerVals = std( [newSigNode{tUse(tN)}(iNo,spikePos{iNo}-3); ...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}-2);...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}-1);...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo});...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}+1);...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}+2);...
                newSigNode{tUse(tN)}(iNo,spikePos{iNo}+3)] );
            
            % Coefficient of variation.
            % Update by Satyam: do not silently pass undefined spike-zone statistics.
            assert(all(lowerVals>0) && all(isfinite(upperVals)), ...
                'FORCe:InvalidFeature','Undefined soft-threshold statistic');
            coefVar{iNo} = upperVals ./ lowerVals;
            
            % Collect...
            allCoefVar = [allCoefVar coefVar{iNo}];
        end
        % For each channel apply soft thresholding.
        for iNo = 1:size( newSigNode{tUse(tN)},1 ),
            T = checkVal * (mean(allCoefVar)+std(allCoefVar));
            for i = 1:length( spikePos{iNo} ),
                if abs(coefVar{iNo}(i)) > T,
                    newSigNode{tUse(tN)}(iNo,spikePos{iNo}(i)) = (adjustVal)*newSigNode{tUse(tN)}(iNo,spikePos{iNo}(i));
                end
            end
        end        
    
    end
    
    % Reconstruct from wavelet decompositions.
    for chNo = 1:size( chData,1 ),
        for tN = 1:length( tUse ),
            wavePacksOut{chNo} = write( wavePacksOut{chNo},'data',tNodes(tUse(tN)),newSigNode{tUse(tN)}(chNo,:) );
        end
    end
    for chNo = 1:size( chData,1 ),
        cleanEEG(chNo,:) = wprec( wavePacksOut{chNo} );
    end

    % The below line can be used to plot the original epoch and the cleaned
    % epoch to check the performance of the method (just add a breakpoint
    % and run it :).
    % clf;t=0:1/Fs:1.0; subplot(2,1,1);hold on;for chNo=1:16,plot(t,EEGdata(chNo,:)-(chNo*50));end;hold off;axis([0 1 -900 0]);subplot(2,1,2);hold on;for chNo=1:16,plot(t,cleanEEG(chNo,:)-(chNo*50));end;hold off;axis([0 1 -900 0]);
    
end
