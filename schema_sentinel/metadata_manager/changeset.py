class ChangeSet:
    def __init__(
        self,
        id,
        author,
        file_name,
        run_manually=False,
        depends_on=None,
        md5sum=None,
        date_executed=None,
        index=0,
        contexts=None,
        approved_by=None,
        jira_ticket=None,
        jira_description=None,
        tag=None,
        description=None,
        run_always=False,
    ):
        self.id = id
        self.author = author
        self.file_name = file_name
        self.run_manually = run_manually
        self.depends_on = depends_on
        self.md5sum = md5sum
        self.date_executed = date_executed
        self.index = index
        self.contexts = contexts
        self.approved_by = approved_by
        self.jira_ticket = jira_ticket
        self.jira_description = jira_description
        self.tag = tag
        self.description = description
        self.run_always = run_always

    def __iter__(self):
        yield self

    def to_string(self):
        return self.__dict__
