#!/bin/bash
#SBATCH --job-name=multinode
#SBATCH --nodes=5
#SBATCH --ntasks-per-node=2
#SBATCH --output=multinode-%j.out
echo "Job \$SLURM_JOB_ID on nodes: \$SLURM_JOB_NODELIST (\$SLURM_NTASKS tasks)"
srun bash -c "echo task \\\$SLURM_PROCID of \\\$SLURM_NTASKS on \\\$(hostname)" | sort -V
