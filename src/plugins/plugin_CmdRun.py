import os
import re
import json
import subprocess

from sl_env import Env
from sl_pluginLoader import PluginLoader
from plugin_Base import PluginBase



class CmdRun(PluginBase):
    def __init__(self, env, name, **kwargs):
        super().__init__(env, name, **kwargs)


    def process(self, **kwargs):
        self.logger.debug("CmdRun start, run_file={}".format(
            kwargs["run_file"]))
        self.__save_initial_state()
        self.__params = kwargs

        return self.__process()



    def __process(self):
        self.run_status = True

        scenario_file = self.__params["run_file"]
        if not os.path.isfile(scenario_file):
            scenario_file = "{}/{}".format(self.env["sl_commands_dir"],
                self.__params["run_file"])
        if not os.path.isfile(scenario_file):
            raise Exception("Can't find run_file {}.".format(
                self.__params["run_file"]))

        self.cmd_env = Env()
        self.cmd_env.append_env(scenario_file)

        if "commands_flow" not in self.cmd_env \
            and "cmd_name" not in self.__params:
            self.logger.error(
                "CmdRun, no command to run, run_file: {}, args: {}".format(
                    scenario_file, self.__params))
            return False

        if "cmd_name" in self.__params:
            if "get_command_only" in self.__params \
                and self.__params["get_command_only"] == True:
                return self.__prepare_command(self.__params["cmd_name"])
            return self.__run_command(self.__params["cmd_name"])

        for command_item in self.cmd_env["commands_flow"]:
            command_name = next(iter(command_item))
            command_ctx = command_item[command_name]

            status = self.__run_command(command_name)

            self.__save_status(status)
            if not self.__check_status(status, command_ctx):
                break

        return self.run_status



    def __save_initial_state(self):
        self.__inital_dir = os.getcwd()



    def __restore_initial_state(self):
        os.chdir(self.__inital_dir)



    def __run_command(self, command_name):
        self.logger.info("running command: {}".format(command_name))
        command = self.__prepare_command(command_name)

        cmd_ctx = self.cmd_env[command_name]
        if "active_dir" in cmd_ctx:
            os.chdir(self.__get_value(cmd_ctx["active_dir"]))


        # 2. start time

        # command execution
        return_code = subprocess.call(command)
        # 3. end time

        if return_code != 0:
            # 1.1 error description
            self.__restore_initial_state()
            return False

        self.__restore_initial_state()
        return True



    def __save_status(self, status):
        # save result to database
        self.run_status = self.run_status and status



    def __check_status(self, status, command_ctx):
        return status



    def __prepare_command(self, command_name):
        cmd_ctx = self.cmd_env[command_name]

        command = []
        command.append(self.__get_value(cmd_ctx["command"]))

        for raw_arg in cmd_ctx["arg_list"]:
            command.append(self.__get_value(raw_arg))
 
        self.logger.debug(command)
        return command 



    def __get_value(self, raw_arg):
        value = raw_arg

        re_subst = re.compile(self.env["re_subst_template"])

        while (True):
            m = re.match(re_subst, value)
            if not m:
                return value

            # (.*)\$\((env|cmd_env|os_env|self_env|param)\:(.+)\)(.*)
            #  1        2                                    3     4
            
            subs_value = ""
            source = m.group(2)
            key = m.group(3)

            if source == "env":
                subs_value = self.env[key]
            elif source == "param":
                subs_value = self.__params[key]
            elif source == "self_env":
                subs_value = self.cmd_env[key]
            else:
                raise Exception("Source '{}' not supported for now".format(
                    source))

            value = m.group(1) + subs_value + m.group(4)


