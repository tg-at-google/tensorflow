/* Copyright 2017 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#ifndef TENSORFLOW_COMPILER_XLA_SERVICE_GPU_GEMM_THUNK_H_
#define TENSORFLOW_COMPILER_XLA_SERVICE_GPU_GEMM_THUNK_H_

#include "tensorflow/compiler/xla/service/buffer_assignment.h"
#include "tensorflow/compiler/xla/service/gpu/backend_configs.pb.h"
#include "tensorflow/compiler/xla/service/gpu/buffer_allocations.h"
#include "tensorflow/compiler/xla/service/gpu/gpu_executable.h"
#include "tensorflow/compiler/xla/service/gpu/hlo_execution_profiler.h"
#include "tensorflow/compiler/xla/service/gpu/thunk.h"
#include "tensorflow/compiler/xla/service/hlo_instruction.h"
#include "tensorflow/compiler/xla/xla_data.pb.h"
#include "tensorflow/core/lib/core/status.h"
#include "tensorflow/core/platform/stream_executor_no_cuda.h"
#include "tensorflow/stream_executor/blas.h"

namespace xla {
namespace gpu {

// This class stores everything that StreamExecutor needs to launch a BLAS gemm.
// It is generated by IrEmitter.
//
// This is thread-compatible.
class GemmThunk : public Thunk {
 public:
  // Constructs a thunk that computes "output = (lhs <dot> rhs) * alpha" using
  // BLAS gemm (alpha is stored in the instruction GemmBackendConfig).
  GemmThunk(ThunkInfo thunk_info, const BufferAllocation::Slice& lhs_buffer,
            const BufferAllocation::Slice& rhs_buffer,
            const BufferAllocation::Slice& output_buffer,
            bool implements_whole_instruction,
            const GemmBackendConfig& backend_config);

  GemmThunk(const GemmThunk&) = delete;
  GemmThunk& operator=(const GemmThunk&) = delete;

  Status ExecuteOnStream(const ExecuteParams& params) override;

 private:
  const BufferAllocation::Slice lhs_buffer_;
  const BufferAllocation::Slice rhs_buffer_;
  const BufferAllocation::Slice output_buffer_;
  bool implements_whole_instruction_;
  GemmBackendConfig backend_config_;
};

// Run the given GEMM instruction `gemm` subject to the configuration
// in `backend_config` and the passed buffers.
//
// `implements_whole_instruction` is used for the default profiler creation
// if the `profiler` is not supplied. False value indicates that the created
// profiler will not specifically profile the `gemm` instruction.
//
// If `algorithm` is provided, it overrides the one specified in
// `backend_config`.
Status RunGemm(
    const HloInstruction* gemm, const GemmBackendConfig& backend_config,
    se::DeviceMemoryBase lhs_buffer, se::DeviceMemoryBase rhs_buffer,
    se::DeviceMemoryBase output_buffer, se::Stream* stream,
    bool implements_whole_instruction, absl::optional<int64> profile_index,
    HloExecutionProfiler* profiler = nullptr,
    se::blas::ProfileResult* profile_result = nullptr,
    absl::optional<se::blas::AlgorithmType> algorithm = absl::nullopt);

}  // namespace gpu
}  // namespace xla

#endif  // TENSORFLOW_COMPILER_XLA_SERVICE_GPU_GEMM_THUNK_H_
