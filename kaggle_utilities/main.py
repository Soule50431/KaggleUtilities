from git import Repo
import subprocess
from pathlib import Path


class GitHub:
    def __init__(self, username, repo_root, name):
        if isinstance(repo_root, str):
            self.repo_root = Path(repo_root)
        elif isinstance(repo_root, Path):
            self.repo_root = repo_root
        self.repo_name = name.split(".")[0]
        self.username = username

    def _run(self, *commands):
        for command in commands:
            subprocess.run(command, shell=True, cwd=self.repo_root)

    def get_repository(self):
        url = f"https://github.com/{self.username}/" + f"{self.repo_name}.git"
        try:
            repo = Repo(self.repo_root)
        except:
            repo = Repo.init(self.repo_root)

            # make .gitignore file
            with open(self.repo_root / ".gitignore", "w") as f:
                f.write("input/\noutput/\n.idea/\n")

            # create remote repository and do first commit
            self._run(
                f"gh repo create {self.repo_name} --confirm --private",
                "git commit --allow-empty -m \"first commit\"",
                "git pull --allow-unrelated-histories origin master ",
                "git push -u origin master"
            )
        return repo

    def commit(self, message=""):
        assert self.repo_root is not None, "Repository root should be set."
        assert self.repo_name is not None, "Repository name should be set."

        repo = self.get_repository()
        repo.git.add(".")
        repo.index.commit(message)
        repo.remote().push("master")



class KaggleDataset:
    def __init__(self, model_root, name):
        if isinstance(model_root, str):
            self.model_root = Path(model_root)
        elif isinstance(model_root, Path):
            self.model_root = model_root
        self.name = name

        assert not (self.model_root/self.name).exists(), "Folder of output model is already exists."
        (self.model_root/self.name).mkdir(parents=True)

    def _run(self, *commands):
        for command in commands:
            subprocess.run(command, shell=True, cwd=self.model_root)

    def _change_metadata(self):
        with open(self.model_root/self.name/"dataset-metadata.json", "r") as f:
            text = f.read()
            text = text.replace("INSERT_TITLE_HERE", self.name).replace("INSERT_SLUG_HERE", self.name)

        with open(self.model_root/self.name/"dataset-metadata.json", "w") as f:
            f.write(text)

    def create_dataset(self):
        self._run(f"kaggle datasets init -p {self.name}")
        self._change_metadata()
        self._run(f"kaggle datasets create -p {self.name}")
