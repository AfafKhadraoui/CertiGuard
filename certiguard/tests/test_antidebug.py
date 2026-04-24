import platform
import sys
import time
from pathlib import Path

# Add src to sys.path to allow direct execution
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    import pytest
except ImportError:
    pytest = None

from certiguard.layers.antidebug import debugger_detected

def test_debugger_detected_normal_run():
    # In a normal test run (assuming we aren't debugging the test itself),
    # this should return False.
    # Note: If the test is run under a debugger (e.g. from an IDE in debug mode),
    # this test will naturally fail, which actually proves it works.
    
    # We will temporarily disable sys.settrace if pytest or coverage is using it
    # just for the context of this specific check if needed, but for simplicity
    # we just run it and assert it doesn't crash.
    
    original_trace = sys.gettrace()
    if original_trace is None:
        # Not under a Python debugger like pdb or PyCharm's debugger
        # So we expect it to be False (unless a native debugger is attached)
        assert debugger_detected() is False

def test_debugger_detected_timing():
    # If we mock the time.perf_counter_ns to simulate a huge delay, it should return True
    import certiguard.layers.antidebug as ad
    
    # Save original
    original_perf = time.perf_counter_ns
    
    # Mock to always return a huge gap
    class MockPerfCounter:
        def __init__(self):
            self.calls = 0
            
        def __call__(self):
            self.calls += 1
            if self.calls == 1:
                return 0
            return 100_000_000 # 100ms
            
    ad.time.perf_counter_ns = MockPerfCounter()
    
    try:
        # Should detect the "timing anomaly"
        assert ad._timing_analysis() is True
    finally:
        # Restore
        ad.time.perf_counter_ns = original_perf

if __name__ == "__main__":
    if pytest:
        sys.exit(pytest.main([__file__]))
    else:
        print("Running tests without pytest...")
        test_debugger_detected_normal_run()
        test_debugger_detected_timing()
        print("All tests passed!")
