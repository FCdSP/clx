# Copyright (c) 2019, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cudf
import pytest
import os
from pathlib import Path
from clx.io.factory.factory import Factory
from clx.io.reader.dask_fs_reader import DaskFileSystemReader

expected_df = cudf.DataFrame(
    {
        "firstname": ["Emma", "Ava", "Sophia"],
        "lastname": ["Olivia", "Isabella", "Charlotte"],
        "gender": ["F", "F", "F"],
    }
)


@pytest.mark.parametrize("expected_df", [expected_df])
def test_fetch_data_csv(tmpdir, expected_df):
    fname = tmpdir.mkdir("tmp_test_fs_reader").join("person.csv")
    expected_df.to_csv(fname, index=False)
    config = {
        "type": "dask_fs",
        "input_path": fname,
        "names": ["firstname", "lastname", "gender"],
        "delimiter": ",",
        "usecols": ["firstname", "lastname", "gender"],
        "dtype": ["str", "str", "str"],
        "header": 0,
        "input_format": "csv",
    }
    reader = DaskFileSystemReader(config)
    fetched_df = reader.fetch_data().compute()

    assert fetched_df.equals(expected_df)

@pytest.mark.parametrize("expected_df", [expected_df])
def test_fetch_data_parquet(tmpdir, expected_df):
    fname = str(tmpdir.mkdir("tmp_test_fs_reader"))
    cudf.io.parquet.to_parquet(expected_df, fname)
    clx_input_path = fname + "/*.parquet"
    config = {
        "type": "dask_fs",
        "input_path": clx_input_path,
        "columns": ["firstname", "lastname", "gender"],
        "input_format": "parquet",
        "gather_statistics":False, 
        "split_row_groups":False
    }

    reader = DaskFileSystemReader(config)
    fetched_df = reader.fetch_data().compute()

    assert fetched_df.equals(expected_df)

@pytest.mark.parametrize("expected_df", [expected_df])
def test_fetch_data_orc(tmpdir, expected_df):
    fname = str(tmpdir.mkdir("tmp_test_fs_reader").join("person.orc"))
    cudf.io.orc.to_orc(expected_df, fname)
    config = {
        "type": "dask_fs",
        "input_path": fname,
        "input_format": "orc"
    }

    reader = DaskFileSystemReader(config)
    fetched_df = reader.fetch_data().compute()

    assert fetched_df.equals(expected_df)