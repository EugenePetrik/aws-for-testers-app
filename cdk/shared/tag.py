from aws_cdk import Tags


def mark(construct):
    Tags.of(construct).add('cloudx', 'qa')
    return construct
