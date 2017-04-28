import json

import pytest

from lazy_build import main


@pytest.fixture
def simple_project(tmpdir):
    tmpdir.join('.lazy-build.json').write(json.dumps({
        'cache': {
            'source': 'filesystem',
            'path': 'cache',
        },
    }))
    tmpdir.join('cache').mkdir()
    tmpdir.join('input').write('first input\n')
    tmpdir.join('test.sh').write(
        'echo ohai\n'
        'cat input > output1\n'
        'mkdir -p output2\n'
        'echo asdf > output2/thing\n'
    )
    with tmpdir.as_cwd():
        yield tmpdir


def test_typical_flow(simple_project, capfd):
    """Test that it correctly caches based on the inputs."""
    args = (
        'build',
        'context=', 'input',
        'output=', 'output1', 'output2',
        'command=', 'bash', 'test.sh',
    )

    def cleanup():
        simple_project.join('output1').remove()
        simple_project.join('output2').remove()

    # The first run shouldn't be cached.
    main.main(args)
    out, err = capfd.readouterr()
    assert out == 'ohai\n'
    assert simple_project.join('output1').read() == 'first input\n'
    assert simple_project.join('output2', 'thing').read() == 'asdf\n'

    # The second run should be cached.
    cleanup()
    main.main(args)
    out, err = capfd.readouterr()
    assert out == ''
    assert simple_project.join('output1').read() == 'first input\n'
    assert simple_project.join('output2', 'thing').read() == 'asdf\n'

    # If we change the input, it shouldn't be cached anymore.
    cleanup()
    simple_project.join('input').write('second input\n')
    main.main(args)
    out, err = capfd.readouterr()
    assert out == 'ohai\n'
    assert simple_project.join('output1').read() == 'second input\n'
    assert simple_project.join('output2', 'thing').read() == 'asdf\n'

    # But the next run with the same input should be cached.
    cleanup()
    main.main(args)
    out, err = capfd.readouterr()
    assert out == ''
    assert simple_project.join('output1').read() == 'second input\n'
    assert simple_project.join('output2', 'thing').read() == 'asdf\n'


def test_after_download_works(simple_project, capfd):
    args = (
        'build', '--verbose',
        'context=', 'input',
        'output=', 'output1', 'output2',
        'after-download=', 'echo', 'it', 'was', 'downloaded',
        'command=', 'bash', 'test.sh',
    )

    # The first run shouldn't be downloaded.
    main.main(args)
    out, err = capfd.readouterr()
    assert out == 'ohai\n'
    lines = err.splitlines()
    assert 'Found no remote build artifact, building locally.' in lines
    assert 'Uploading artifact to shared cache...' in lines

    # The second run should be.
    main.main(args)
    out, err = capfd.readouterr()
    assert out == 'it was downloaded\n'
    lines = err.splitlines()
    assert 'Found remote build artifact, downloading.' in lines
    assert 'Running after-download script...' in lines
