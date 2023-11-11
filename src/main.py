import os
import re
from libs.github.github_client import GitHubClient
from dotenv import load_dotenv


class Main:
    def __init__(self):
        self.current_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.pj_dir = os.path.dirname(self.current_dir_path)

        # mdファイル内の画像を格納するディレクトリ
        self.images_dir = f'{self.pj_dir}/images'
        # GitHubの画像URLに置き換えたいmdファイルを格納するディレクトリ
        self.input_md_files_dir = f'{self.pj_dir}/input_md_files'
        # 画像URL変換後のmdファイルを格納するディレクトリ
        self.output_md_files_dir = f'{self.pj_dir}/output_md_files'

        # .envから環境変数を取得
        self.secrets = self.get_secrets()

        # GitHubクライアントの初期化
        self.github_client = GitHubClient(
            access_token=self.secrets['GITHUB_ACCESS_TOKEN']
        )

        # GitHubAPI用の設定
        self.github_repo_owner = self.secrets['GITHUB_REPO_OWNER']
        self.github_repo_name = self.secrets['GITHUB_REPO_NAME']

    def get_secrets(self) -> dict:
        load_dotenv(dotenv_path=f'{self.pj_dir}/.env')
        return os.environ

    def convert_image_using_github(self, image_path, output_path) -> str:
        # 対象の画像がGitHubにアップロードされていれば、そのURLを返す
        try:
            response = self.github_client.get_contents(
                repo_owner=self.github_repo_owner,
                repo_name=self.github_repo_name,
                file_path=output_path
            )
            return response['download_url']
        except Exception as e:
            print(e)

        # 画像をアップロード
        response = self.github_client.upload_image(
            repo_owner=self.github_repo_owner,
            repo_name=self.github_repo_name,
            image_path=image_path,
            output_path=output_path,
        )

        github_image_url = response['content']['download_url']

        return github_image_url

    def main(self):
        # 各mdファイルを処理
        md_file_name_list = os.listdir(self.input_md_files_dir)
        for md_file_name in md_file_name_list:
            # mdファイル以外はスキップ
            if not md_file_name.endswith('.md'):
                continue

            print(f'{md_file_name}の処理を開始します。')

            # mdファイルを読み込み
            md_file_path = f'{self.input_md_files_dir}/{md_file_name}'
            with open(md_file_path, 'r') as f:
                md_text = f.read()

            # mdファイルから画像パス一覧を取得
            image_file_path_pattern = re.compile(r'!\[.*\]\((.*)\)')
            image_file_path_list = image_file_path_pattern.findall(md_text)

            # /images/から始まる画像パスのみ抽出
            image_file_path_list = list(filter(lambda x: x.startswith('/images/'), image_file_path_list))

            print(image_file_path_list)

            # 画像を一つずつ処理
            for image_file_path in image_file_path_list:
                image_file_abs_path = f'{self.pj_dir}{image_file_path}'

                # /images/以降のパスで画像をアップロードする
                output_path = image_file_path.replace('/images/', '')

                # GitHubから画像URLを取得
                image_url = self.convert_image_using_github(
                    image_path=image_file_abs_path,
                    output_path=output_path,
                )

                print(image_url)

                # GitHubの画像URLに置換
                md_text = md_text.replace(
                    image_file_path,
                    image_url
                )

            # mdファイルを出力
            new_md_file_path = f'{self.output_md_files_dir}/{md_file_name}'
            with open(new_md_file_path, 'w') as f:
                f.write(md_text)


if __name__ == '__main__':
    main = Main()
    main.main()
