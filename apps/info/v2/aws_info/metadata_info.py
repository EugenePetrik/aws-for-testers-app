"""Module to work with ec2 metadata"""

from ec2_metadata import ec2_metadata


def get_info() -> dict:
    """Retrieves ec2 info from instance metadata"""

    return {'region': ec2_metadata.region,
            'availability_zone': ec2_metadata.availability_zone}
