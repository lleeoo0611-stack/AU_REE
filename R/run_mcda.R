#!/usr/bin/env Rscript
# Five-stage Australian REE MCDA: AHP, PROMETHEE II, SAW, TOPSIS, Monte Carlo.
# No hidden imputation; research judgment matrices are required for authoritative ranks.
options(stringsAsFactors = FALSE)
args <- commandArgs(trailingOnly=TRUE)
getarg <- function(key, default=NULL) { i <- which(args==key); if(length(i)==0) return(default); if(i==length(args)) stop(paste('Missing value for',key));args[i+1] }
flag <- function(key) key %in% args
input <- getarg('--input'); dictionary <- getarg('--criteria'); weights_path <- getarg('--weights')
perspective <- getarg('--perspective','development_driven'); out <- getarg('--out','outputs/r_results')
ahp_path <- getarg('--ahp'); illustrative <- flag('--illustrative')
seed <- as.integer(getarg('--seed','20261029')); nreps <- as.integer(getarg('--reps','1000'))
if(is.null(input)||is.null(dictionary)||is.null(weights_path)) stop('Require --input --criteria --weights')
if(!file.exists(input)) stop(paste('Missing decision matrix:',input))
df <- read.csv(input,check.names=FALSE,fileEncoding='UTF-8-BOM')
if(nrow(df)<2) stop('Not enough MCDA-eligible alternatives; no ranking was generated.')
dict <- read.csv(dictionary,fileEncoding='UTF-8-BOM');wdf <- read.csv(weights_path,fileEncoding='UTF-8-BOM')
codes <- intersect(dict$criterion,names(df)); if(length(codes)<2) stop('Insufficient criteria')
X <- as.matrix(df[,codes,drop=FALSE]); storage.mode(X)<-'double'
if(any(!is.finite(X))) stop('Decision matrix contains missing/unverified values: no imputation permitted.')
if(anyDuplicated(df$project_id)) stop('Duplicate project_id in decision matrix')
weights <- wdf[wdf$perspective==perspective & wdf$criterion %in% codes,,drop=FALSE]
if(nrow(weights)!=length(codes)||anyDuplicated(weights$criterion)) stop('Scenario weights do not cover active criteria')
weights <- weights[match(codes,weights$criterion),]
if(any(!is.finite(weights$weight))||any(weights$weight<0)||sum(weights$weight)<=0) stop('Invalid scenario weights')
w <- weights$weight/sum(weights$weight)
AHP <- function(path,codes,max_cr=0.10){
  pairs <- read.csv(path,fileEncoding='UTF-8-BOM'); req <- c('criterion_a','criterion_b','ratio')
  if(!all(req %in% names(pairs))) stop('AHP file requires criterion_a,criterion_b,ratio')
  n <- length(codes); A<-diag(n); rownames(A)<-colnames(A)<-codes
  seen <- matrix(FALSE,n,n,dimnames=list(codes,codes));diag(seen)<-TRUE
  for(i in seq_len(nrow(pairs))){a<-pairs$criterion_a[i];b<-pairs$criterion_b[i];r<-as.numeric(pairs$ratio[i])
    if(!(a%in%codes)||!(b%in%codes))next
    if(!is.finite(r)||r<=0)stop('AHP ratio must be positive')
    if(seen[a,b])stop(paste('Repeated AHP comparison',a,b))
    A[a,b]<-r;A[b,a]<-1/r;seen[a,b]<-seen[b,a]<-TRUE
  }
  if(any(!seen))stop('AHP judgments incomplete; provide all criterion pairs')
  ww<-exp(rowMeans(log(A)));ww<-ww/sum(ww)
  lambda<-mean(as.vector((A%*%ww)/ww));CI<-if(n>1)(lambda-n)/(n-1) else 0
  ri<-c(0,0,0.58,0.90,1.12,1.24,1.32,1.41,1.45,1.49,1.51,1.48,1.56,1.57,1.59)
  if(n>length(ri))stop('AHP n > 15 not supported')
  CR<-if(ri[n]==0)0 else CI/ri[n]
  if(CR>max_cr)stop(sprintf('AHP inconsistency CR=%.4f exceeds threshold %.2f',CR,max_cr))
  list(weights=ww,CR=CR,lambda=lambda)
}
status <- 'RESEARCHER_AHP'
if(!is.null(ahp_path)){
  a<-AHP(ahp_path,codes);w<-a$weights; cat('AHP CR:',format(a$CR,digits=4),'\n')
}else if(illustrative){status <- 'ILLUSTRATIVE_ASSUMED_WEIGHTS';cat('ILLUSTRATIVE WEIGHTS: NOT AHP-ELICITED\n')
}else{stop('Provide --ahp judged_pairwise.csv or explicitly --illustrative (not publication-authoritative).')}
orient<-dict$direction[match(codes,dict$criterion)]
sgn<-ifelse(orient=='MAX',1,-1)
# V-shape thresholds derive from frozen point matrix. Fixed multiplier documented.
threshold<-apply(X,2,IQR);width<-apply(X,2,function(v)diff(range(v)))
threshold[threshold<=0]<-width[threshold<=0];threshold[threshold<=0]<-1
PROMETHEE <- function(X,w,sgn,p){n<-nrow(X); total<-matrix(0,n,n)
 for(j in seq_len(ncol(X))){d<-outer(X[,j],X[,j],'-')*sgn[j]
  total<-total+w[j]*pmin(1,pmax(0,d/p[j]))}
 diag(total)<-0; plus<-rowSums(total)/(n-1);minus<-colSums(total)/(n-1)
 plus-minus}
SAW<-function(X,w,sgn){Z<-X;for(j in seq_len(ncol(X))){v<-X[,j];ran<-diff(range(v));Z[,j]<-if(ran==0)1 else if(sgn[j]==1)(v-min(v))/ran else (max(v)-v)/ran};as.vector(Z%*%w)}
TOPSIS<-function(X,w,sgn){Z<-X;for(j in seq_len(ncol(X))){norm<-sqrt(sum(X[,j]^2));Z[,j]<-if(norm>0)X[,j]/norm else 0};Z<-sweep(Z,2,w,'*');upper<-lower<-numeric(ncol(X));for(j in seq_len(ncol(X))){upper[j]<-if(sgn[j]==1)max(Z[,j]) else min(Z[,j]);lower[j]<-if(sgn[j]==1)min(Z[,j]) else max(Z[,j])};pos<-sqrt(rowSums(sweep(Z,2,upper,'-')^2));neg<-sqrt(rowSums(sweep(Z,2,lower,'-')^2));ifelse(pos+neg==0,0.5,neg/(pos+neg))}
score<-PROMETHEE(X,w,sgn,threshold)
res<-data.frame(project_id=df$project_id,project_name=df$project_name,
 promethee_net_flow=score,promethee_rank=rank(-score,ties.method='min'),
 saw_score=SAW(X,w,sgn),topsis_score=TOPSIS(X,w,sgn))
res$saw_rank<-rank(-res$saw_score,ties.method='min');res$topsis_rank<-rank(-res$topsis_score,ties.method='min')
set.seed(seed)
if(is.na(nreps)||nreps<1||nreps>100000)stop('Invalid --reps')
concentration<-30
R <- matrix(NA_real_,nrow(X),nreps)
for(i in seq_len(nreps)){
 wt<-rgamma(length(w),shape=pmax(0.001,w*concentration),rate=1);wt<-wt/sum(wt)
 R[,i]<-rank(-PROMETHEE(X,wt,sgn,threshold),ties.method='average')
}
res$rank_median<-apply(R,1,median);res$rank_q05<-apply(R,1,quantile,probs=0.05);
res$rank_q95<-apply(R,1,quantile,probs=0.95);res$p_top3<-rowMeans(R<=3);res$p_top5<-rowMeans(R<=5)
# Leave one criterion out: Spearman correlation to full ranking.
loo<-data.frame(criterion_removed=codes,rank_spearman=NA_real_)
for(j in seq_along(codes)){
 if(length(w)<3)next
 idx<-setdiff(seq_along(w),j);ww<-w[idx]/sum(w[idx]);p<-PROMETHEE(X[,idx,drop=FALSE],ww,sgn[idx],threshold[idx]);
 loo$rank_spearman[j]<-suppressWarnings(cor(rank(-score),rank(-p),method='spearman'))
}
dir.create(out,recursive=TRUE,showWarnings=FALSE)
write.csv(res,file.path(out,'ranking_comparison.csv'),row.names=FALSE,na='')
write.csv(loo,file.path(out,'leave_one_out.csv'),row.names=FALSE,na='')
sensitivity <- do.call(rbind,lapply(c(0.5,1.0,2.0),function(m){sc<-PROMETHEE(X,w,sgn,threshold*m);data.frame(threshold_multiplier=m,spearman_to_baseline=suppressWarnings(cor(rank(-score),rank(-sc),method='spearman')))}))
write.csv(sensitivity,file.path(out,'threshold_sensitivity.csv'),row.names=FALSE)
write.csv(data.frame(criterion=codes,weight=w,threshold=threshold,status=status),file.path(out,'weight_and_threshold_audit.csv'),row.names=FALSE)
write.csv(data.frame(project_id=df$project_id,R,check.names=FALSE),file.path(out,'monte_carlo_ranks.csv'),row.names=FALSE)
cat('Completed',nrow(X),'alternatives,',length(codes),'criteria,',nreps,'MC draws.\n')
cat('Weight status:',status,'\n')
