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
